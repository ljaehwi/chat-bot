# back/graph/nodes/check_with_8b.py
from langchain_core.messages import SystemMessage, HumanMessage
from ..state import AgentState
from ...prompts import CHECK_8B_PROMPT, CHECK_8B_SYSTEM_PROMPT

async def check_with_8b(state: AgentState, llm):
    """
    Generates a draft answer using the local 8B model.
    """
    state["current_node"] = "check_with_8b"
    log_message = "---NODE: Generate Draft Answer with 8B Model---"
    state["log"] = [log_message]
    print(log_message) # Keep print for now

    user_prompt = CHECK_8B_PROMPT.format(
        user_intent=state.get('rewritten_prompt', state.get('user_intent')),
        tool_results=state.get('tool_results', 'No tool results.')
    )
    
    messages = [
        SystemMessage(content=CHECK_8B_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
    response = await llm.ainvoke(messages)
    return {"final_answer": response.content}
