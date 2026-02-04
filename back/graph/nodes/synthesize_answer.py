# back/graph/nodes/synthesize_answer.py
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..state import AgentState
from ...prompts import CHECK_8B_PROMPT, CHECK_8B_SYSTEM_PROMPT

async def synthesize_answer(state: AgentState, llm):
    """
    Synthesizes the results from tool execution into a natural language answer.
    This node sets the 'final_answer' key in the state for validation.
    """
    state["current_node"] = "synthesize_answer"
    log_message = "---NODE: Synthesize Answer---"
    state["log"] = [log_message]
    print(log_message)

    user_intent = state.get("rewritten_prompt", "")
    tool_results = state.get("tool_results", "")

    print(f"  > Synthesizing answer for intent: {user_intent}")
    print(f"  > Using tool results: {tool_results}")

    prompt = CHECK_8B_PROMPT.format(
        user_intent=user_intent,
        tool_results=tool_results
    )

    messages = [
        SystemMessage(content=CHECK_8B_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]

    response = await llm.ainvoke(messages)
    final_answer = response.content

    print(f"  > Synthesized Answer (to be validated): {final_answer}")

    # Set the final_answer for the validation node
    return {"final_answer": final_answer}
