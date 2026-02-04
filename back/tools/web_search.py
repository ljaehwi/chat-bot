import os
import asyncio
from typing import Dict, Any, List
from tavily import TavilyClient

class WebSearchTool:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        self.client = TavilyClient(api_key=self.api_key)
    
    async def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        웹 검색을 수행하고 결과를 반환합니다.
        """
        try:
            # Tavily 클라이언트는 동기식이므로 비동기로 실행
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.search(
                    query=query,
                    search_depth="basic",
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False
                )
            )
            
            # 결과 포맷팅
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")[:500] + "..." if len(result.get("content", "")) > 500 else result.get("content", "")
                })
            
            return {
                "query": query,
                "answer": response.get("answer", ""),
                "results": results,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "status": "error"
            }

# 전역 인스턴스
web_search_tool = None

def get_web_search_tool():
    global web_search_tool
    if web_search_tool is None:
        try:
            web_search_tool = WebSearchTool()
        except Exception as e:
            print(f"Failed to initialize WebSearchTool: {e}")
            web_search_tool = None
    return web_search_tool