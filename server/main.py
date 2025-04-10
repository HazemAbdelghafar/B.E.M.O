from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from websocket_manager import connection_manager
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utilities import TEST

# === Payload schema for sending messages to robot ===
class RobotMessage(BaseModel):
    message: str

app = FastAPI()

# Allow cross-origin access for clients or UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === WebSocket route for robot connection ===
@app.websocket("/ws/{robot_id}")
async def websocket_endpoint(websocket: WebSocket, robot_id: str):
    await connection_manager.connect(robot_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[{robot_id}] says: {data}")
            # Send a response back to the robot
            try:
                await connection_manager.send_message(robot_id, f"Sending {TEST} to {robot_id}")
            except Exception as e:
                print(f"Error sending message to {robot_id}: {e}")
                connection_manager.disconnect(robot_id)
                break
    except WebSocketDisconnect:
        connection_manager.disconnect(robot_id)
        print(f"[{robot_id}] disconnected.")

# === HTTP route to send message to a specific robot ===
@app.post("/send/{robot_id}")
async def send_to_robot(robot_id: str, payload: RobotMessage):
    if not connection_manager.is_connected(robot_id):
        raise HTTPException(status_code=404, detail=f"Robot '{robot_id}' not connected")

    await connection_manager.send_message(robot_id, payload.message)
    return JSONResponse(content={"status": "sent", "robot_id": robot_id, "message": payload.message})
