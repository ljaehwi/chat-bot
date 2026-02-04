# back/graph/nodes/clarify_intent.py
from langchain_core.messages import SystemMessage, HumanMessage

from ...prompts import INTENT_CLASSIFIER_PROMPT, INTENT_CLASSIFIER_SYSTEM_PROMPT

from ..state import AgentState



async def clarify_intent(state: AgentState, llm):
    """
    Clarifies the user's intent.
    """
    state["current_node"] = "clarify_intent"
    log_message = "---NODE: Clarify User Intent---"
    state["log"] = [log_message]
    print(log_message) # Keep print for now for visibility during development

    

    user_message = state["messages"][-1].content

    

    # Create the prompt

    intent_prompt = INTENT_CLASSIFIER_PROMPT.format(user_message=user_message)

    

    messages = [

        SystemMessage(content=INTENT_CLASSIFIER_SYSTEM_PROMPT),

        HumanMessage(content=intent_prompt)

    ]

    

    response = await llm.ainvoke(messages)

    

    return {"user_intent": response.content.strip()}
