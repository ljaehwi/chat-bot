# back/graph/nodes/call_gemini.py
from langchain_core.messages import SystemMessage, HumanMessage
from sqlmodel.ext.asyncio.session import AsyncSession

from ..state import AgentState
from ...db import crud
from ...db.engine import async_engine
from ...prompts import GEMINI_FALLBACK_PROMPT, GEMINI_FALLBACK_SYSTEM_PROMPT
from ...utils.rate_limiter import rate_limited_gemini

@rate_limited_gemini
async def call_gemini(state: AgentState, llm):
    """
    Calls the Gemini model as a fallback and saves the response for distillation.
    """
    state["current_node"] = "call_gemini"
    log_message = "---NODE: Call Gemini as Fallback---"
    state["log"] = [log_message]
    print(log_message)

    if state.get("gemini_unavailable"):
        fallback_log = ">> Gemini unavailable, using local model answer"
        state["log"].append(fallback_log)
        print(fallback_log)
        return {"final_answer": state.get("final_answer", "죄송합니다. 현재 답변을 생성할 수 없습니다.")}

    user_intent_str = state.get('user_intent', 'unknown')
    original_query = state['messages'][0].content
    tool_results_str = state.get('tool_results', 'No tool results.')
    
    user_prompt = GEMINI_FALLBACK_PROMPT.format(
        user_intent=user_intent_str,
        tool_results=tool_results_str
    )
    
    messages = [
        SystemMessage(content=GEMINI_FALLBACK_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        response = await llm.ainvoke(messages)
        gemini_answer = response.content
        
        distillation_log = "---DISTILLATION: Saving Gemini response for later---"
        state["log"].append(distillation_log)
        print(distillation_log)

        # Save to knowledge distillation table
        async with AsyncSession(async_engine) as session:
            await crud.create_knowledge_distillation(
                session=session,
                query=original_query,
                intent=user_intent_str,
                gemini_response=gemini_answer,
                local_model_failure_reason=state.get("tool_results", "") # Pass the validator's reason
            )
        
        return {"final_answer": gemini_answer}
        
    except Exception as e:
        error_log = f">> Gemini call failed: {e}"
        state["log"].append(error_log)
        print(error_log)
        return {"final_answer": state.get("final_answer", "죄송합니다. 현재 답변을 생성할 수 없습니다.")}
