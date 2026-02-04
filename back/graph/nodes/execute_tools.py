# back/graph/nodes/execute_tools.py
import json
from ..state import AgentState, ToolResult

async def execute_tools(state: AgentState, tools):
    """
    Executes the planned tool calls.
    """
    state["current_node"] = "execute_tools"
    log_message = "---NODE: Execute Tools---"
    state["log"] = [log_message]
    print(log_message) # Keep print for now

    plan = state.get("plan", [])
    tool_results = []
    for tool_call in plan:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Log which tool is being executed
        execution_log = f"Executing tool: {tool_name} with args: {tool_args}"
        state["log"].append(execution_log)
        print(execution_log)

        lc_tool = next((t for t in tools if t.name == tool_name), None)
        if lc_tool:
            try:
                # Assuming the tool's coroutine method exists
                result = await lc_tool.coroutine(**tool_args)
                tool_results.append(ToolResult(tool_name=tool_name, output=json.dumps(result, ensure_ascii=False, indent=2)))
            except Exception as e:
                error_log = f"Error executing tool {tool_name}: {e}"
                state["log"].append(error_log)
                print(error_log)
                tool_results.append(ToolResult(tool_name=tool_name, output=f"Error: {e}"))
        else:
            not_found_log = f"Tool '{tool_name}' not found."
            state["log"].append(not_found_log)
            print(not_found_log)
            tool_results.append(ToolResult(tool_name=tool_name, output="Tool not found."))
            
    return {"tool_results": tool_results}
