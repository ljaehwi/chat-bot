from functools import partial
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes.clarify_intent import clarify_intent
from .nodes.initial_planner import initial_planner
from .nodes.db_search import db_search
from .nodes.update_user_profile import update_user_profile
from .nodes.execute_tools import execute_tools
from .nodes.synthesize_answer import synthesize_answer
from .nodes.check_with_8b import check_with_8b
from .nodes.validate_answer import validate_answer
from .nodes.call_gemini import call_gemini
from .nodes.give_final_answer import give_final_answer

from ..tools.manager import MCPToolManager

# --- Conditional Edges (Routing Logic) ---

def route_after_intent(state: AgentState) -> str:
    """Routes to the correct node based on the classified user intent."""
    intent = state.get("user_intent", "Chat")
    if intent == "Profile":
        print("  > ?덉쉵堉?琉?筌??덉슦萸?? Updating User Profile")
        return "update_user_profile"
    else:
        print(f"  > ?덉쉵堉?琉?筌??덉슦萸?? Proceeding with '{intent}' plan")
        return "db_search"

def should_use_db_result(state: AgentState) -> str:
    """
    If DB hit, return answer; otherwise continue to tool planning.
    """
    if state.get("db_hit"):
        return "give_final_answer"
    return "initial_planner"

def should_execute_tools(state: AgentState) -> str:
    """If the tool queue has items, execute next tool; otherwise move on."""
    if state.get("tool_queue") and len(state.get("tool_queue", [])) > 0:
        print("  > ?덉쉵堉?琉?筌??덉슦萸?? Executing Next Tool")
        return "execute_tools"
    else:
        print("  > ?덉쉵堉?琉?筌??덉슦萸?? No Tools, Going to Chat")
        return "check_with_8b"

def should_continue_tools(state: AgentState) -> str:
    """If tools remain, keep executing; otherwise synthesize or chat."""
    if state.get("tool_queue") and len(state.get("tool_queue", [])) > 0:
        return "execute_tools"
    if state.get("tool_results") and len(state.get("tool_results", [])) > 0:
        return "synthesize_answer"
    return "check_with_8b"

def is_answer_satisfactory(state: AgentState) -> str:
    """Routes based on the validation result from the Gemini judge."""
    if state.get("gemini_unavailable"):
        return "give_final_answer"
    
    if state.get("is_final_answer_satisfactory"):
        return "give_final_answer"
    else:
        return "call_gemini"

# --- Graph Definition ---

async def create_graph(tool_manager: MCPToolManager):
    # 1. Initialize Models
    local_llm = ChatOllama(model="exaone3.5", temperature=0)
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    
    # 2. Get Tools
    tools = await tool_manager.get_langchain_tools()

    workflow = StateGraph(AgentState)
    
    # --- Add Nodes ---
    workflow.add_node("clarify_intent", partial(clarify_intent, llm=local_llm))
    workflow.add_node("db_search", db_search)
    workflow.add_node("initial_planner", partial(initial_planner, llm=local_llm, tools=tools))
    workflow.add_node("update_user_profile", partial(update_user_profile, llm=local_llm))
    workflow.add_node("execute_tools", partial(execute_tools, tools=tools))
    workflow.add_node("synthesize_answer", partial(synthesize_answer, llm=local_llm))
    workflow.add_node("check_with_8b", partial(check_with_8b, llm=local_llm))
    workflow.add_node("validate_answer", partial(validate_answer, llm=gemini_llm))
    workflow.add_node("call_gemini", partial(call_gemini, llm=gemini_llm))
    workflow.add_node("give_final_answer", give_final_answer)

    # --- Define Edges ---
    workflow.set_entry_point("clarify_intent")
    
    # 1. After clarifying intent, route based on whether it's a profile update or other task
    workflow.add_conditional_edges(
        "clarify_intent",
        route_after_intent,
        {
            "update_user_profile": "update_user_profile",
            "db_search": "db_search"
        }
    )

    workflow.add_conditional_edges(
        "db_search",
        should_use_db_result,
        {
            "give_final_answer": "give_final_answer",
            "initial_planner": "initial_planner"
        }
    )
    
    # 2. The profile node goes directly to the end
    workflow.add_edge("update_user_profile", "give_final_answer")

    # 3. Execute tools in queue order (if any)
    workflow.add_conditional_edges(
        "initial_planner",
        should_execute_tools,
        {
            "execute_tools": "execute_tools",
            "check_with_8b": "check_with_8b"
        }
    )

    # 4. Tool queue loop: execute until empty
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue_tools,
        {
            "execute_tools": "execute_tools",
            "synthesize_answer": "synthesize_answer",
            "check_with_8b": "check_with_8b"
        }
    )

    workflow.add_edge("synthesize_answer", "validate_answer")
    workflow.add_edge("check_with_8b", "validate_answer")
    
    workflow.add_conditional_edges(
        "validate_answer", 
        is_answer_satisfactory,
        {
            "give_final_answer": "give_final_answer",
            "call_gemini": "call_gemini"
        }
    )
    
    workflow.add_edge("call_gemini", "give_final_answer")
    workflow.add_edge("give_final_answer", END)
    
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)
