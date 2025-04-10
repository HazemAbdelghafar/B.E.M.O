from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from websocket_manager import connection_manager
from pathlib import Path
import sys

app = FastAPI()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utilities import TEST


# Optional: Allow CORS if needed (e.g., robot on different domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{robot_id}")
async def websocket_endpoint(websocket: WebSocket, robot_id: str):
    print(TEST)
    await connection_manager.connect(robot_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[{robot_id}] says: {data}")
            # Optionally respond or process
    except WebSocketDisconnect:
        connection_manager.disconnect(robot_id)
        print(f"[{robot_id}] disconnected.")
