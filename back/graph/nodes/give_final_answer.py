# back/graph/nodes/give_final_answer.py
from langchain_core.messages import AIMessage
from ..state import AgentState

async def give_final_answer(state: AgentState):
    """
    Provides the final answer to the user.
    """
    state["current_node"] = "give_final_answer"
    log_message = "---NODE: Give Final Answer---"
    state["log"] = [log_message]
    print(log_message)

    final_answer = state.get("final_answer", "I'm sorry, I couldn't find an answer.")
    # The last message is the final answer.
    # We clear the log here as it's the end of the run.
    return {"messages": [AIMessage(content=final_answer)], "log": []}
