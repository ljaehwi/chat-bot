# back/main.py

# 1. External Imports
import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, List
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# 2. Internal Imports
from back.db import crud
from back.db.engine import async_engine, get_session, init_db
from back.graph.graph import create_graph
from back.tools.manager import MCPToolManager
from back.health_checks import run_all_health_checks

# 3. Shared Variables
tool_manager: MCPToolManager | None = None
graph: Any = None
summarizer_llm: Any = None
health_status: Dict[str, Any] = {}
background_tasks: Dict[str, asyncio.Task] = {}

# 4. Shared Functions (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global tool_manager, graph, summarizer_llm, health_status
    
    print("\n--- [System] Running Startup Health Checks ---")
    await init_db() 
    
    # Run checks
    db_ok, ollama_ok, gemini_ok = await run_all_health_checks(async_engine)
    
    health_status['db'] = {'status': 'ok' if db_ok[0] else 'error', 'message': db_ok[1]}
    health_status['local_llm'] = {'status': 'ok' if ollama_ok[0] else 'error', 'message': ollama_ok[1]}
    health_status['gemini_llm'] = {'status': 'ok' if gemini_ok[0] else 'error', 'message': gemini_ok[1]}

    # Print Status
    for service, status in health_status.items():
        color = "\033[92m" if status['status'] == 'ok' else "\033[91m"
        reset = "\033[0m"
        print(f"  {color}[{status['status'].upper()}]{reset} {service.upper()}: {status['message']}")
    
    print("\n--- [System] Initializing Components ---")
    
    # 1. MCP Tool Manager Init
    print("  > Initializing MCP Tool Manager...")
    tool_manager = MCPToolManager()
    await tool_manager.initialize()
    
    # MCP 연결 확인 로그
    if tool_manager.sessions:
        print(f"  \033[92m[OK]\033[0m MCP Connected: {len(tool_manager.sessions)} servers active.")
        # 로드된 툴 목록 출력 (디버깅용)
        tools = await tool_manager.get_langchain_tools()
        tool_names = [t.name for t in tools]
        print(f"  > Loaded Tools: {tool_names}")
    else:
        print("  \033[91m[WARN]\033[0m No MCP servers connected. Check 'mcp_server_config.json'.")

    # 2. Graph Init
    print("  > Creating Agent Graph...")
    graph = await create_graph(tool_manager)
    
    # 3. Summarizer Init (모델 버전 수정됨: 1.5 -> 2.5)
    print("  > Initializing Summarizer LLM...")
    try:
        summarizer_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    except Exception as e:
        print(f"  \033[91m[FAIL]\033[0m Summarizer Init failed: {e}")

    print("\033[92m--- Application startup complete. Ready to serve. ---\033[0m\n")
    
    yield
    
    print("\n--- [System] Shutting down... ---")
    if tool_manager:
        await tool_manager.cleanup()
        print("  > MCP connections closed.")


# 5. Pydantic Models
class RunRequest(BaseModel):
    user_id: int = Field(..., description="User ID must be an integer (e.g., 1)")
    message: str
    thread_id: Optional[str] = None

class RunResponse(BaseModel):
    thread_id: str
    status: str

class StopRequest(BaseModel):
    thread_id: str


# 6. FastAPI App Initialization
app = FastAPI(title="Personal AI Assistant Agent", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 7. Helper Functions
async def _summarize_if_needed(thread_id: str, db: AsyncSession):
    """
    Placeholder for summarization logic.
    In a real scenario, this would check chat volume and trigger summarization.
    """
    # 현재는 에러 방지용으로 비워둠 (추후 구현)
    pass


# 8. API Endpoints

@app.get("/")
async def root():
    return {
        "system": "Personal AI Agent",
        "status": "operational",
        "health": health_status
    }

# The /api/agent/run endpoint is now removed as all execution happens over WebSocket.

@app.post("/api/agent/stop")
async def agent_stop(request: StopRequest):
    task = background_tasks.get(request.thread_id)
    if task and not task.done():
        task.cancel()
        return {"status": "stopped"}
    return {"status": "not_running"}


@app.get("/api/agent/{thread_id}/state")
async def get_agent_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.get_state(config)
    if not state:
        raise HTTPException(status_code=404, detail="Thread not found")
    return state.values


@app.get("/api/system/health")
async def system_health():
    return {
        "components": health_status,
        "mcp_tools": len(tool_manager.sessions) if tool_manager else 0
    }


# 9. WebSocket Endpoint (Real-time Chat)
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time chat with the agent.
    Each message from a client starts a new, independent agent run.
    """
    await websocket.accept()
    print("[WS] Client connected")

    try:
        while True:
            # 1. Receive Message
            data = await websocket.receive_text()
            print(f"[WS] Received: {data}")
            
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON format"})
                continue
            
            user_message = payload.get("message")
            if not user_message:
                await websocket.send_json({"type": "error", "content": "No message provided"})
                continue

            try:
                user_id = int(payload.get("user_id", 1))
            except (ValueError, TypeError):
                user_id = 1
            
            print(f"[WS] Processing message: '{user_message}' from user {user_id}")
            
            # ALWAYS create a new thread_id for each run to ensure a clean state.
            thread_id = str(uuid.uuid4())

            # 2. Setup Graph Config
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "user_id": user_id
                }
            }

            # Get a new DB session for this interaction
            async with AsyncSession(async_engine) as session:
                # 0. Check DB for an existing matching answer
                existing_answer = await crud.find_similar_answer(session, user_message)
                if existing_answer:
                    await websocket.send_json({
                        "type": "final_answer",
                        "content": existing_answer.content
                    })
                    await websocket.send_json({"type": "end"})
                    # Save user message + reused assistant answer
                    await crud.create_chat_history(session, intent="db_cache", role="user", content=user_message)
                    await crud.create_chat_history(session, intent="db_cache", role="assistant", content=existing_answer.content)
                    continue

                # 1. Load recent chat history for context (last 5 messages)
                recent_history = await crud.get_recent_chat_history(session, limit=5)
                recent_history = list(reversed(recent_history)) if recent_history else []

                context_messages = []
                for item in recent_history:
                    if item.role == "user":
                        context_messages.append(HumanMessage(content=item.content))
                    else:
                        context_messages.append(AIMessage(content=item.content))

                # 3. Setup initial state (without db_session to avoid pickle error)
                initial_state = {
                    "messages": context_messages + [HumanMessage(content=user_message)],
                    "user_id": user_id,
                    "log": [],
                }

                # Save user message to DB
                # TODO: The 'intent' is not yet classified here. We'll use a placeholder.
                await crud.create_chat_history(session, intent="unknown", role="user", content=user_message)

                try:
                    # 4. Execute Graph and Stream Results
                    current_response = ""
                    async for event in graph.astream_events(initial_state, config=config, version="v1"):
                        kind = event["event"]
                        
                        # Node start/end notifications
                        if kind == "on_chain_start":
                            node_name = event.get("name", "unknown")
                            await websocket.send_json({
                                "type": "node_start",
                                "content": f"🔄 {node_name} 실행 중...",
                                "node": node_name
                            })
                        
                        elif kind == "on_chain_end":
                            node_name = event.get("name", "unknown")
                            await websocket.send_json({
                                "type": "node_end",
                                "content": f"✅ {node_name} 완료",
                                "node": node_name
                            })
                        
                        # LLM streaming
                        elif kind == "on_chat_model_stream":
                            content = event["data"]["chunk"].content
                            if content:
                                current_response += content
                                await websocket.send_json({"type": "thinking", "content": "..."})
                        
                        # Tool execution notifications
                        elif kind == "on_tool_start":
                            await websocket.send_json({
                                "type": "tool_start",
                                "content": f"🛠️ {event['name']} 실행 중..."
                            })
                        
                        elif kind == "on_tool_end":
                            await websocket.send_json({
                                "type": "tool_end",
                                "content": f"✔️ {event['name']} 완료"
                            })
                    
                    # 5. Get final state and send final answer
                    final_state = await graph.aget_state(config)
                    final_answer_content = "죄송합니다. 답변을 생성하지 못했습니다." # Default
                    if final_state:
                        # The final answer is now stored in the 'final_answer' key
                        final_answer_content = final_state.values.get("final_answer", final_answer_content)

                    # Send the final answer with tool metadata
                    tool_results = final_state.values.get("tool_results", []) if final_state else []
                    await websocket.send_json({
                        "type": "final_answer", 
                        "content": final_answer_content,
                        "tool_results": tool_results
                    })

                    # Save AI message to DB
                    # TODO: Get the actual intent from the final_state
                    final_intent = final_state.values.get("user_intent", "unknown")
                    await crud.create_chat_history(session, intent=final_intent, role="assistant", content=final_answer_content)
                    
                    # 6. Finish Turn
                    await websocket.send_json({"type": "end"})
                
                except Exception as graph_error:
                    print(f"[WS] Graph execution error: {graph_error}")
                    await websocket.send_json({
                        "type": "error", 
                        "content": f"처리 중 오류가 발생했습니다: {str(graph_error)}"
                    })
                    await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        print(f"[WS] Error: {e}")
        try:
            await websocket.send_json({"type": "error", "content": f"서버 오류: {str(e)}"})
        except:
            pass
        await websocket.close()
