# back/graph/nodes/translate_to_english.py
from langchain_core.messages import HumanMessage
from ..state import AgentState
from ...prompts import TRANSLATE_TO_ENGLISH_PROMPT

async def translate_to_english(state: AgentState, llm):
    print("---NODE: Translate to English---")
    
    user_message = state["messages"][-1].content
    
    prompt = TRANSLATE_TO_ENGLISH_PROMPT.format(text=user_message)
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    # We replace the last message with the translated one
    new_messages = state["messages"][:-1] + [HumanMessage(content=response.content, id=state["messages"][-1].id)]
    
    return {"messages": new_messages}
