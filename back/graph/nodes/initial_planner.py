# back/graph/nodes/initial_planner.py
import json
from ..state import AgentState

async def initial_planner(state: AgentState):
    """
    Creates a deterministic, initial tool plan based on the classified user intent.
    This node does not use an LLM.
    """
    state["current_node"] = "initial_planner"
    log_message = "---NODE: Initial Planner---"
    state["log"] = [log_message]
    print(log_message) 

    intent = state.get("user_intent", "Chat")
    user_message = state["messages"][-1].content
    plan = []

    print(f"  > Intent: {intent}")
    print(f"  > User Message: {user_message}")

    if intent == "Search":
        plan = [{"name": "web_search", "args": {"query": user_message}}]
    elif intent == "Database":
        # Placeholder for a database search tool
        # For now, we can use web_search as a fallback or define a specific db tool
        plan = [{"name": "db_search", "args": {"query": user_message}}]
    elif intent == "System":
        # This is a simplification. A real scenario might need to parse the command.
        plan = [{"name": "shell_command", "args": {"command": user_message}}]
    else: # Chat
        plan = []

    print(f"  > Initial Plan: {plan}")

    # The 'plan' from this node will be used by 'execute_tools'
    # The 'rewritten_prompt' is no longer necessary as we use the original message
    return {
        "plan": plan,
        "rewritten_prompt": user_message 
    }
