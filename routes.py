from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict
from datetime import datetime, timezone
import logging
import json
from fastapi.responses import HTMLResponse
from jinja2 import Template
import asyncio

# === Logging ===
logger = logging.getLogger("uvicorn")

# === Router setup ===
router = APIRouter(prefix="/api")

# === Constants ===
SERVER_ID = "server"

# === Connection tracking ===
connected_devices: Dict[str, WebSocket] = {}
device_metadata: Dict[str, Dict] = {}

# === Utility ===

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def get_duration_seconds(connected_at_iso: str):
    connected_at = datetime.fromisoformat(connected_at_iso)
    now = datetime.now(timezone.utc)
    return int((now - connected_at).total_seconds())

async def send_safe(ws: WebSocket, data: dict):
    if ws.client_state == WebSocketState.CONNECTED:
        try:
            await ws.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    else:
        logger.warning("Attempted to send on a closed socket.")

async def forward_message_to_robot(target_id: str, message: str):
    sender_id = SERVER_ID
    
    if target_id in connected_devices:
        await send_safe(connected_devices[target_id], json.loads(message))
        logger.info(f"Forwarded from {sender_id} to {target_id}: {message}")
    else:
        logger.warning(f"Target '{target_id}' not connected.")
       
        await send_safe(connected_devices[sender_id], {
            "error": f"Target '{target_id}' not connected.",
            "level": 3,
            "src_robot_id": target_id,
            "is_server_error": True
        })


async def start_ping_loop(ws: WebSocket, device_id: str, interval: int = 30):
    try:
        while ws.client_state == WebSocketState.CONNECTED:
            await asyncio.sleep(interval)
            if device_id in connected_devices:
                await send_safe(connected_devices[device_id], {"type": "ping"})
    except Exception as e:
        logger.warning(f"Ping loop error for {device_id}: {e}")

# === WebSocket Endpoint ===

@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")
    await websocket.accept()

    ip = websocket.client.host
    connected_at = now_utc_iso()

    asyncio.create_task(start_ping_loop(websocket, id))  # Start ping task

    if id == SERVER_ID:
        if SERVER_ID in connected_devices:
            old_ws = connected_devices[SERVER_ID]
            logger.warning("Server already connected. Replacing it.")
            try:
                await send_safe(old_ws, {
                    "warning": "Another server has replaced this connection.",
                })
                await old_ws.close()
            except Exception as e:
                logger.error(f"Error closing old server connection: {e}")

        connected_devices[SERVER_ID] = websocket
        device_metadata[SERVER_ID] = {"ip": ip, "connected_at": connected_at}
        logger.info(f"Server connected from {ip}")

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"Server sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON from server.")
                    await send_safe(websocket, {"error": "Invalid JSON Format", "level": 3})
                    continue

                if data.get("type") == "ping":
                    continue  # Ignore pings

                target_id = data.get("target_robot_id")
                if target_id:
                    await forward_message_to_robot(target_id, message)
                else:
                    logger.warning("No 'target_robot_id' in message.")

        except WebSocketDisconnect:
            logger.warning("Server disconnected.")
        finally:
            logger.warning("Cleaning up all robot connections since server disconnected.")
            robot_ids = [rid for rid in connected_devices if rid != SERVER_ID]
            for rid in robot_ids:
                try:
                    await send_safe(connected_devices[rid], {
                        "error": "Server disconnected. Closing robot connection.",
                        "level": 3,
                        "is_server_error": True
                    })
                    await connected_devices[rid].close()
                    logger.info(f"Disconnected robot: {rid}")
                except Exception as e:
                    logger.error(f"Failed to disconnect robot {rid}: {e}")
                finally:
                    connected_devices.pop(rid, None)
                    device_metadata.pop(rid, None)

            duration = get_duration_seconds(device_metadata[SERVER_ID]["connected_at"])
            logger.info(f"Server was connected for {duration} seconds")

            connected_devices.pop(SERVER_ID, None)
            device_metadata.pop(SERVER_ID, None)

    else:
        if SERVER_ID not in connected_devices:
            logger.error("Server not connected. Rejecting robot.")
            await send_safe(websocket, {
                "error": "Server not connected.",
                "level": 3,
                "target_robot_id": id,
                "is_server_error": True
            })
            await websocket.close()
            return

        connected_devices[id] = websocket
        device_metadata[id] = {"ip": ip, "connected_at": connected_at}
        logger.info(f"Robot '{id}' connected from {ip}")

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"{id} sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from robot {id}.")
                    await send_safe(websocket, {
                        "error": "Invalid JSON Format",
                        "level": 3,
                        "target_robot_id": id,
                        "is_server_error": True
                    })
                    continue

                if data.get("type") == "ping":
                    continue  # Ignore pings

                await send_safe(connected_devices[SERVER_ID], data)
                logger.info(f"Forwarded message from {id} to server.")

        except WebSocketDisconnect:
            logger.warning(f"Robot '{id}' disconnected.")
        finally:
            metadata = device_metadata.get(id, {})
            connected_at = metadata.get("connected_at")

            if connected_at:
                duration = get_duration_seconds(connected_at)
                logger.info(f"Robot '{id}' was connected for {duration} seconds")
            else:
                logger.warning(f"No 'connected_at' info for robot '{id}'")

            connected_devices.pop(id, None)
            device_metadata.pop(id, None)            
# === REST Endpoint for status ===

@router.get("/connected-devices", response_class=HTMLResponse)
async def get_connected_devices():
    def format_device(device_id, info):
        duration = get_duration_seconds(info["connected_at"])
        return {
            "id": device_id,
            "ip": info["ip"],
            "connected_at": info["connected_at"],
            "duration": duration
        }

    server_info = (
        format_device(SERVER_ID, device_metadata[SERVER_ID])
        if SERVER_ID in device_metadata else None
    )

    robots = [
        format_device(device_id, info)
        for device_id, info in device_metadata.items()
        if device_id != SERVER_ID
    ]

    html_template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BEMO Connected Devices</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 30px; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
            th { background-color: #eee; }
            .status-ok { color: green; font-weight: bold; }
            .status-bad { color: red; font-weight: bold; }
            .meta { margin-top: 10px; font-size: 14px; color: #555; }
        </style>
    </head>
    <body>
        <h1>BEMO Connection Dashboard</h1>

        <h2>Server</h2>
        {% if server %}
            <div class="meta">
                <strong>Status:</strong> <span class="status-ok">Connected</span><br>
                <strong>IP:</strong> {{ server.ip }}<br>
                <strong>Connected at:</strong> {{ server.connected_at }}<br>
                <strong>Duration:</strong> {{ server.duration }} sec
            </div>
        {% else %}
            <div class="meta">
                <strong>Status:</strong> <span class="status-bad">Disconnected</span>
            </div>
        {% endif %}

        <h2>Robots ({{ robots|length }})</h2>
        {% if robots %}
        <table>
            <tr>
                <th>ID</th>
                <th>IP</th>
                <th>Connected At</th>
                <th>Duration (sec)</th>
            </tr>
            {% for robot in robots %}
            <tr>
                <td>{{ robot.id }}</td>
                <td>{{ robot.ip }}</td>
                <td>{{ robot.connected_at }}</td>
                <td>{{ robot.duration }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No robots connected.</p>
        {% endif %}
    </body>
    </html>
    """)

    html = html_template.render(server=server_info, robots=robots)
    return HTMLResponse(content=html)
