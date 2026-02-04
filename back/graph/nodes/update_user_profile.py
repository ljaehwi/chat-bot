# back/graph/nodes/update_user_profile.py
import json
from langchain_core.messages import SystemMessage, HumanMessage
from sqlmodel.ext.asyncio.session import AsyncSession

from ..state import AgentState
from ...db import crud
from ...db.engine import async_engine
from ...prompts import PROFILE_EXTRACTOR_SYSTEM_PROMPT, PROFILE_EXTRACTOR_PROMPT

def _clean_llm_output(llm_output: str) -> str:
    """Helper function to clean the typical markdown JSON from LLM output."""
    if '```json' in llm_output:
        return llm_output.split('```json')[1].split('```')[0].strip()
    if '```' in llm_output:
        return llm_output.split('```')[1].split('```')[0].strip()
    return llm_output

async def update_user_profile(state: AgentState, llm):
    """
    Extracts personal information from the user's message, updates the user's
    profile in the database, and generates a confirmation message.
    """
    state["current_node"] = "update_user_profile"
    log_message = "---NODE: Update User Profile (DEBUG)---"
    state["log"] = [log_message]
    print(log_message)

    user_message = state['messages'][-1].content
    user_id = state['user_id']
    
    # 1. Extract info from the message using an LLM
    extraction_prompt = PROFILE_EXTRACTOR_PROMPT.format(user_message=user_message)
    messages = [
        SystemMessage(content=PROFILE_EXTRACTOR_SYSTEM_PROMPT),
        HumanMessage(content=extraction_prompt)
    ]
    # NOTE: The error might be happening inside this llm.ainvoke call or a library it uses.
    response = await llm.ainvoke(messages)
    
    # --- DEBUGGING: Temporarily simplify the rest of the function ---
    
    # extracted_info = {}
    # try:
    #     cleaned_output = _clean_llm_output(response.content)
    #     extracted_info = json.loads(cleaned_output)
    #     print(f"  > Extracted Profile Info: {extracted_info}")
    # except Exception as e:
    #     print(f"  > Error parsing profile JSON: {e}")
    #     print(f"  > LLM output was: {response.content}")

    # # 2. Update DB and generate confirmation
    # confirmation_message = "알겠습니다. (임시)" # Default confirmation

    # if extracted_info:
    #     # async with AsyncSession(async_engine) as session:
    #     #     updated_user = await crud.update_user(session, user_id=user_id, new_info_dict=extracted_info)
        
    #     # if updated_user:
    #     #     # Create a more specific confirmation message
    #     #     info_str = ", ".join([f"'{k}'은(는) '{v}'" + "(으)로" for k, v in extracted_info.items()])
    #     #     confirmation_message = f"알겠습니다. 사용자님의 정보({info_str})를 기억하겠습니다."
    
    confirmation_message = f"임시 답변: LLM이 생성한 내용은 다음과 같습니다: {response.content}"

    print(f"  > Confirmation Message: {confirmation_message}")

    # 3. Set final_answer and skip to the end
    return {"final_answer": confirmation_message}
