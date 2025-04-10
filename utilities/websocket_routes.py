from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

router = APIRouter(prefix="/api")

connected_robots: Dict[str, WebSocket] = {}

@router.websocket("/ws/{robot_id}")
async def websocket_endpoint(websocket: WebSocket, robot_id: str):
    await websocket.accept()
    connected_robots[robot_id] = websocket
    print(f"✅ Robot connected: {robot_id}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"📥 {robot_id} says: {data}")
    except WebSocketDisconnect:
        print(f"❌ {robot_id} disconnected")
        connected_robots.pop(robot_id, None)
