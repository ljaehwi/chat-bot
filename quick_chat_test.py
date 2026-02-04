import asyncio
import websockets
import json

async def test_chat():
    try:
        async with websockets.connect("ws://localhost:8000/ws/chat") as websocket:
            print("[OK] WebSocket 연결 성공")
            
            # 테스트 메시지 전송
            test_message = {
                "message": "안녕하세요",
                "user_id": 1
            }
            
            await websocket.send(json.dumps(test_message))
            print("[SEND] 메시지 전송:", test_message["message"])
            
            # 응답 받기
            timeout_count = 0
            while timeout_count < 10:  # 10초 타임아웃
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    print(f"[RECV] {data['type']}: {data.get('content', '')}")
                    
                    if data['type'] == 'end':
                        break
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print("[WAIT] 응답 대기 중...")
                    
    except ConnectionRefusedError:
        print("[ERROR] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"[ERROR] 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())