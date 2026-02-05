# back/graph/nodes/db_search.py
from ..state import AgentState, ToolResult
from ...db.engine import async_engine
from ...db import crud
from sqlmodel.ext.asyncio.session import AsyncSession

async def db_search(state: AgentState):
    """
    Search DB for a similar answer before using external tools.
    """
    state["current_node"] = "db_search"
    log_message = "---NODE: DB Search---"
    state["log"] = [log_message]
    print(log_message)

    user_message = state["messages"][-1].content
    async with AsyncSession(async_engine) as session:
        match = await crud.find_similar_answer(session, user_message)

    if match:
        tool_results = state.get("tool_results") or []
        tool_results.append(ToolResult(
            tool_name="db_search",
            output=match.content
        ))
        return {
            "db_hit": True,
            "final_answer": match.content,
            "tool_results": tool_results
        }

    return {"db_hit": False}
