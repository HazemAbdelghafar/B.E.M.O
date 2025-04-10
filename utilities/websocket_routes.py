from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio

router = APIRouter(prefix="/api")

connected_robots: Dict[str, WebSocket] = {}

@router.websocket("/ws/{robot_id}")
async def websocket_endpoint(websocket: WebSocket, robot_id: str):
    print(f"🤖 New connection: {robot_id}")
    asyncio.sleep(0.1)  # Simulate some delay
    await websocket.accept()
    connected_robots[robot_id] = websocket
    print(f"✅ Robot connected: {robot_id}")
    asyncio.sleep(0.1)  # Simulate some delay

    try:
        while True:
            data = await websocket.receive_text()
            print(f"📥 {robot_id} says: {data}")
            asyncio.sleep(0.1)
            # Respond to the robot
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print(f"❌ {robot_id} disconnected")
        asyncio.sleep(0.1)
        connected_robots.pop(robot_id, None)
