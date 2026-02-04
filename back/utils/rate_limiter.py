import asyncio
import time
from typing import Dict, Any
from functools import wraps

class RateLimiter:
    def __init__(self, calls_per_minute: int = 15):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        async with self.lock:
            now = time.time()
            # 1분 이전 호출 기록 제거
            self.calls = [call_time for call_time in self.calls if now - call_time < 60]
            
            if len(self.calls) >= self.calls_per_minute:
                # 가장 오래된 호출로부터 60초 대기
                wait_time = 60 - (now - self.calls[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # 대기 후 다시 정리
                    now = time.time()
                    self.calls = [call_time for call_time in self.calls if now - call_time < 60]
            
            self.calls.append(now)

# 전역 rate limiter
gemini_limiter = RateLimiter(calls_per_minute=15)

def rate_limited_gemini(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await gemini_limiter.wait_if_needed()
        return await func(*args, **kwargs)
    return wrapper