#!/usr/bin/env python3
"""
Simple WebSocket test client for the AI Agent
"""
import asyncio
import json
import websockets
import sys

async def test_websocket():
    uri = "ws://localhost:8000/ws/chat"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 연결 성공!")
            
            # 테스트 메시지 전송
            test_message = {
                "message": "안녕하세요, 테스트입니다.",
                "user_id": 1
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 메시지 전송: {test_message['message']}")
            
            # 응답 수신
            print("📥 응답 수신 중...")
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "token":
                        print(data["content"], end="", flush=True)
                    elif data.get("type") == "log":
                        print(f"\n🔧 {data['content']}")
                    elif data.get("type") == "end":
                        print("\n✅ 응답 완료")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n⏰ 응답 시간 초과")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("\n❌ 연결이 종료되었습니다")
                    break
                    
    except ConnectionRefusedError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("   실행 명령: python run.py")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print("🤖 AI Agent WebSocket 테스트 클라이언트")
    print("=" * 50)
    
    asyncio.run(test_websocket())

if __name__ == "__main__":
    main()