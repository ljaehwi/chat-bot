# back/graph/nodes/execute_tools.py
import json
from typing import Any
from ..state import AgentState, ToolResult

def _jsonable_tool_result(result: Any):
    if result is None:
        return None
    if isinstance(result, (str, int, float, bool, list, dict)):
        return result
    for attr in ("model_dump", "dict"):
        if hasattr(result, attr):
            try:
                return getattr(result, attr)()
            except Exception:
                pass
    for attr in ("content", "data", "output", "result"):
        if hasattr(result, attr):
            try:
                value = getattr(result, attr)
                if isinstance(value, (str, int, float, bool, list, dict)):
                    return value
                return str(value)
            except Exception:
                pass
    return str(result)

async def execute_tools(state: AgentState, tools):
    """
    Executes the planned tool calls.
    """
    state["current_node"] = "execute_tools"
    log_message = "---NODE: Execute Tools---"
    state["log"] = [log_message]
    print(log_message) # Keep print for now

    tool_queue = state.get("tool_queue") or []
    plan = state.get("plan", []) or []
    if tool_queue:
        plan = [tool_queue[0]]
    tool_results = []
    for tool_call in plan:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Log which tool is being executed
        execution_log = f"Executing tool: {tool_name} with args: {tool_args}"
        state["log"].append(execution_log)
        print(execution_log)

        lc_tool = next((t for t in tools if t.name == tool_name), None)
        if lc_tool is None:
            # Fallback: allow tool names without server prefix (e.g., "write_file")
            suffix = f"__{tool_name}"
            candidates = [t for t in tools if t.name.endswith(suffix)]
            if candidates:
                lc_tool = candidates[0]
                state["log"].append(f"Resolved tool alias '{tool_name}' -> '{lc_tool.name}'")
                print(f"Resolved tool alias '{tool_name}' -> '{lc_tool.name}'")
        if lc_tool:
            try:
                # Assuming the tool's coroutine method exists
                result = await lc_tool.coroutine(**tool_args)
                safe_result = _jsonable_tool_result(result)
                tool_results.append(ToolResult(
                    tool_name=tool_name,
                    output=json.dumps(safe_result, ensure_ascii=False, indent=2)
                ))
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
            
    existing_results = state.get("tool_results") or []
    remaining_queue = tool_queue[1:] if tool_queue else tool_queue
    return {
        "tool_results": existing_results + tool_results,
        "tool_queue": remaining_queue
    }
