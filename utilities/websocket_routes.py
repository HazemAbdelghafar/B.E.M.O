from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import random
import time
import logging
import json

# ✅ Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

random.seed(time.time())

friendly_responses = [
    "Hello! I'm here to assist you.",
    "Greetings! How can I help you today?",
    "Hi there! What can I do for you?",
    "Hey! Ready to assist you.",
    "Hello! How may I help you today?"
]

router = APIRouter(prefix="/api")

connected_robots: Dict[str, WebSocket] = {}

@router.websocket("/ws/{robot_id}")
async def websocket_endpoint(websocket: WebSocket, robot_id: str):
    logger.info(f"🤖 New connection: {robot_id}")
    await websocket.accept()
    connected_robots[robot_id] = websocket
    logger.info(f"✅ Robot connected: {robot_id}")

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            logger.info(f"📥 {robot_id} says: {data}")
            await websocket.send_text(friendly_responses[int(data["index"])])
    except WebSocketDisconnect:
        logger.warning(f"❌ {robot_id} disconnected")
        connected_robots.pop(robot_id, None)
