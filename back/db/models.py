from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

class User(SQLModel, table=True):
    """
    Table to store user information and system specifications.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    info: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(SQLModel, table=True):
    """
    Table to store all conversation history.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    intent: str = Field(index=True, description="The intent of the conversation")
    role: str = Field(description="Role of the message sender (user/assistant)")
    content: str = Field(description="Content of the message")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DailySummary(SQLModel, table=True):
    """
    Table to store daily summaries. One row per day.
    """
    date: datetime = Field(primary_key=True, description="The date of the summary")
    summary_content: str = Field(description="The content of the daily summary")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeDistillation(SQLModel, table=True):
    """
    Table to store distilled knowledge for training/fine-tuning.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    query: str = Field(description="The user query")
    intent: str = Field(description="The identified intent")
    gemini_response: str = Field(description="The response from the advanced model (Gemini)")
    local_model_failure_reason: Optional[str] = Field(default=None, description="Reason why local model failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
