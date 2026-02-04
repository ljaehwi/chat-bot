# back/graph/nodes/translate_to_korean.py
from langchain_core.messages import AIMessage, HumanMessage
from ..state import AgentState
from ...prompts import TRANSLATE_TO_KOREAN_PROMPT

async def translate_to_korean(state: AgentState, llm):
    print("---NODE: Translate to Korean---")
    
    final_answer = state.get("final_answer", "I'm sorry, I couldn't find an answer.")
    
    prompt = TRANSLATE_TO_KOREAN_PROMPT.format(text=final_answer)
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return {"messages": [AIMessage(content=response.content)]}
