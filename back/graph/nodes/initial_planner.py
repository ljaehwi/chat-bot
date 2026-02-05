# back/graph/nodes/initial_planner.py
import json
from langchain_core.messages import SystemMessage, HumanMessage
from ..state import AgentState
from ...prompts import TOOL_PLANNER_PROMPT, TOOL_PLANNER_SYSTEM_PROMPT

def _safe_tool_schema(tool):
    if not getattr(tool, "args_schema", None):
        return {}
    try:
        return tool.args_schema.schema()
    except Exception:
        try:
            return tool.args_schema.model_json_schema()
        except Exception:
            return {}

def _extract_json_array(text: str):
    if not text:
        return None
    start = text.find('[')
    end = text.rfind(']')
    if start == -1 or end == -1 or end <= start:
        return None
    snippet = text[start:end + 1]
    try:
        return json.loads(snippet)
    except Exception:
        return None

async def initial_planner(state: AgentState, llm, tools):
    """
    Creates an ordered tool queue for sequential execution.
    """
    state["current_node"] = "initial_planner"
    log_message = "---NODE: Initial Planner---"
    state["log"] = [log_message]
    print(log_message)

    intent = state.get("user_intent", "Chat")
    user_message = state["messages"][-1].content
    print(f"  > Intent: {intent}")
    print(f"  > User Message: {user_message}")

    plan = []
    if intent in ["Search", "Database", "System"]:
        tools_payload = []
        for tool in tools:
            schema = _safe_tool_schema(tool)
            tools_payload.append({
                "name": tool.name,
                "description": tool.description or "",
                "args_schema": schema.get("properties", schema)
            })

        prompt = TOOL_PLANNER_PROMPT.format(
            user_intent=intent,
            user_message=user_message,
            tools_json=json.dumps(tools_payload, ensure_ascii=False, indent=2)
        )

        messages = [
            SystemMessage(content=TOOL_PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]

        try:
            response = await llm.ainvoke(messages)
            raw = (response.content or "").strip()
            if not raw:
                raise ValueError("Empty response from tool planner LLM")

            try:
                plan = json.loads(raw)
            except Exception:
                extracted = _extract_json_array(raw)
                if extracted is None:
                    raise ValueError(f"Invalid JSON response: {raw[:200]}")
                plan = extracted

            if isinstance(plan, dict):
                plan = plan.get("plan", [])

            if not isinstance(plan, list):
                raise ValueError("Tool plan is not a JSON array")

        except Exception as e:
            print(f"  > Tool planning failed, falling back to heuristic plan: {e}")
            if intent == "Search":
                plan = [{"name": "web_search", "args": {"query": user_message}}]
            else:
                plan = []

    print(f"  > Initial Plan: {plan}")

    return {
        "tool_queue": plan,
        "plan": [],
        "rewritten_prompt": user_message
    }
