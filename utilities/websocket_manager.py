from typing import Dict
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, robot_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[robot_id] = websocket
        print(f"Connected: {robot_id}")

    def disconnect(self, robot_id: str):
        if robot_id in self.active_connections:
            del self.active_connections[robot_id]
            print(f"Disconnected: {robot_id}")

    async def send_message(self, robot_id: str, message: str):
        websocket = self.active_connections.get(robot_id)
        if websocket:
            await websocket.send_text(message)

    def is_connected(self, robot_id: str) -> bool:
        return robot_id in self.active_connections

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)

connection_manager = WebSocketManager()
