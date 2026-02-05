import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, create_model

# Internal Imports
from .web_search import get_web_search_tool

class WebSearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Maximum number of results")

class MCPToolManager:
    """
    Manages connections to MCP servers and exposes their tools to LangGraph.
    """
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.servers_config = self._load_config()
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("mcpServers", {})
        except FileNotFoundError:
            return {}

    async def initialize(self):
        """
        Connects to all defined MCP servers.
        """
        for name, config in self.servers_config.items():
            command = config.get("command")
            args = config.get("args", [])
            env = config.get("env", {})
            
            # Resolve env vars in config
            final_env = os.environ.copy()
            for k, v in env.items():
                if v.startswith("${") and v.endswith("}"):
                    var_name = v[2:-1]
                    final_env[k] = os.getenv(var_name, "")
                else:
                    final_env[k] = v

            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=final_env
            )

            try:
                # Start the server transport
                transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                read, write = transport
                
                # Create the session
                session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                self.sessions[name] = session
                print(f"[MCP] Connected to server: {name}")
            except Exception as e:
                print(f"[MCP] Failed to connect to {name}: {e}")

    async def get_langchain_tools(self) -> List[StructuredTool]:
        """
        Fetches tools from all connected MCP servers and converts them to LangChain tools.
        """
        all_tools = []
        
        # Add built-in web search tool
        web_tool = get_web_search_tool()
        if web_tool:
            async def web_search_func(query: str, max_results: int = 5):
                return await web_tool.search(query, max_results)
            
            web_search_tool = StructuredTool.from_function(
                func=None,
                coroutine=web_search_func,
                name="web_search",
                description="Search the web for current information",
                args_schema=WebSearchInput
            )
            all_tools.append(web_search_tool)
        
        # Add MCP tools
        for server_name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                for tool in result.tools:
                    tool_schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None) or {}
                    schema_props = tool_schema.get("properties", {}) if isinstance(tool_schema, dict) else {}
                    required = set(tool_schema.get("required", [])) if isinstance(tool_schema, dict) else set()

                    if schema_props:
                        fields = {}
                        for key, spec in schema_props.items():
                            description = spec.get("description", "") if isinstance(spec, dict) else ""
                            default_value = ... if key in required else None
                            fields[key] = (Any, Field(default_value, description=description))
                        args_schema = create_model(f"{server_name}_{tool.name}_Schema", **fields)
                    else:
                        args_schema = None

                    async def _tool_func(
                        session=session, 
                        tool_name=tool.name, 
                        **kwargs
                    ):
                        return await session.call_tool(tool_name, arguments=kwargs)

                    lc_tool = StructuredTool.from_function(
                        func=None,
                        coroutine=_tool_func,
                        name=f"{server_name}__{tool.name}",
                        description=tool.description or "",
                        args_schema=args_schema
                    )
                    all_tools.append(lc_tool)
            except Exception as e:
                print(f"[MCP] Failed to get tools from {server_name}: {e}")
        
        return all_tools

    async def cleanup(self):
        """
        Closes all connections.
        """
        await self.exit_stack.aclose()
