from typing import List, Optional
from datetime import date, datetime

from sqlalchemy import cast, Date
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import models

async def create_chat_history(session: AsyncSession, intent: str, role: str, content: str) -> None:
    """
    Saves a single chat message to the database.
    """
    db_msg = models.ChatHistory(
        intent=intent,
        role=role,
        content=content
    )
    session.add(db_msg)
    await session.commit()


async def get_chat_history(session: AsyncSession, target_date: date, limit: int = 5) -> List[models.ChatHistory]:
    """
    Retrieves chat history for a specific date.
    Args:
        target_date: The date to filter by (usually today).
        limit: Number of messages to retrieve (default 5).
    """
    statement = (
        select(models.ChatHistory)
        .where(cast(models.ChatHistory.created_at, Date) == target_date)
        .order_by(models.ChatHistory.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def get_recent_chat_history(session: AsyncSession, limit: int = 5) -> List[models.ChatHistory]:
    """
    Retrieves the most recent chat messages (across all dates).
    """
    statement = (
        select(models.ChatHistory)
        .order_by(models.ChatHistory.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def find_similar_answer(session: AsyncSession, query: str) -> Optional[models.ChatHistory]:
    """
    Finds a recent assistant answer that likely matches the query.
    Naive keyword match using ILIKE.
    """
    statement = (
        select(models.ChatHistory)
        .where(models.ChatHistory.role == "assistant")
        .where(models.ChatHistory.content.ilike(f"%{query}%"))
        .order_by(models.ChatHistory.created_at.desc())
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def create_knowledge_distillation(
    session: AsyncSession, 
    query: str, 
    intent: str, 
    gemini_response: str, 
    local_model_failure_reason: str = ""
) -> None:
    """
    Saves a distilled piece of knowledge from Gemini's response.
    """
    distillation_entry = models.KnowledgeDistillation(
        query=query,
        intent=intent,
        gemini_response=gemini_response,
        local_model_failure_reason=local_model_failure_reason
    )
    session.add(distillation_entry)
    await session.commit()
    

async def create_daily_summary(session: AsyncSession, summary_date: date, summary_content: str) -> None:
    """
    Creates or updates a daily summary.
    """
    summary = models.DailySummary(date=summary_date, summary_content=summary_content)
    session.add(summary)
    await session.commit()


async def get_daily_summary(session: AsyncSession, summary_date: date) -> models.DailySummary:
    """
    Retrieves a daily summary for a specific date.
    """
    statement = select(models.DailySummary).where(models.DailySummary.date == summary_date)
    result = await session.execute(statement)
    return result.scalars().first()


async def get_user(session: AsyncSession, user_id: int = 1) -> models.User:
    """
    Retrieves a user by their ID.
    For now, it just gets the first user.
    """
    statement = select(models.User).where(models.User.id == user_id)
    result = await session.execute(statement)
    return result.scalars().first()

async def update_user(session: AsyncSession, user_id: int, new_info_dict: dict) -> models.User:
    """
    Updates a user's profile information.
    """
    user = await get_user(session, user_id)
    if not user:
        # Or create a new user, for now we assume user 1 exists
        return None 
    
    # Merge new info into existing info
    user.info.update(new_info_dict)
    
    # Mark as modified to ensure JSONB updates are picked up
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(user, "info")

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
