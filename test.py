# 먼저 라이브러리 설치가 필요합니다: pip install python-dotenv asyncpg

import asyncio
import os
import asyncpg
from dotenv import load_dotenv

# 현재 디렉토리의 .env 파일 로드
load_dotenv()

async def check_connection():
    # 환경변수 로드 및 검증
    db_config = {
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "database": os.getenv("POSTGRES_DB"),
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.getenv("POSTGRES_PORT", "5433"))
    }

    print(f"Loaded Configuration: User={db_config['user']}, Host={db_config['host']}, DB={db_config['database']}")

    try:
        print("Connecting...")
        conn = await asyncio.wait_for(
            asyncpg.connect(**db_config),
            timeout=5.0  # 5초 타임아웃
        )
        res = await conn.fetchval("SELECT 1")
        print(f"OK 연결 성공! (Response: {res})")
        await conn.close()
    except Exception as e:
        print(f"ERROR 연결 실패\n에러 내용: {e}")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_connection())