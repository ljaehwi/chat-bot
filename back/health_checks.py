# back/health_checks.py
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI

async def check_db_connection(engine: AsyncEngine):
    """
    Checks if the database connection is valid.
    """
    try:
        async with engine.connect() as conn:
            await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))
        return True, "Database connection successful."
    except Exception as e:
        return False, f"Database connection failed: {e}"

async def check_ollama_connection(model_name: str = "exaone3.5"):
    """
    Checks if the connection to the Ollama server is valid.
    """
    try:
        ollama = Ollama(model=model_name)
        await ollama.ainvoke("Hi")
        return True, f"Ollama ({model_name}) connection successful."
    except Exception as e:
        return False, f"Ollama ({model_name}) connection failed: {e}"

async def check_gemini_connection(model_name: str = "gemini-2.5-flash"):
    """
    Checks if the connection to the Gemini API is valid.
    """
    try:
        gemini = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        response = await gemini.ainvoke("Hello")
        return True, f"Gemini ({model_name}) connection successful."
    except Exception as e:
        return False, f"Gemini ({model_name}) connection failed: {e}"

async def run_all_health_checks(engine: AsyncEngine):
    """
    Runs all health checks in parallel.
    """
    results = await asyncio.gather(
        check_db_connection(engine),
        check_ollama_connection(),
        check_gemini_connection(),
    )
    return results
