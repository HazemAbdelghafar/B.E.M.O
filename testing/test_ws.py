import json
import threading
import time
from websocket import WebSocketApp

class RobotWebSocketClient:
    def __init__(self, id: str, server_url: str, max_retries=5, retry_interval=5):
        self.id = id
        self.server_url = server_url + id
        self.ws = None  # WebSocket reference
        self.max_retries = max_retries  # Maximum number of retries
        self.retry_interval = retry_interval  # Time between retries in seconds
        self.retry_count = 0  # Track the number of retries

    def on_open(self, socket):
        self.ws = socket
        print(f"Connected to server with robot {self.id}")

    def on_message(self, socket, message):
        print(f"Message from server: {message}")

    def on_error(self, socket, error):
        print(f"Error: {error}")

    def on_close(self, socket, close_status_code, close_msg):
        print(f"Connection closed")
        # Retry logic when connection closes
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            print(f"Attempting to reconnect ({self.retry_count}/{self.max_retries})...")
            time.sleep(self.retry_interval)
            self.start_connection()  # Attempt to reconnect
        else:
            print("Max retries reached. Connection failed permanently.")

    def start_connection(self):
        """Start the WebSocket connection in a separate thread"""
        ws_app = WebSocketApp(
            self.server_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        # Run WebSocket in its own thread
        thread = threading.Thread(target=ws_app.run_forever)
        thread.daemon = True
        thread.start()

        # Give it a second to connect
        time.sleep(1)

    def send_data(self, payload: dict):
        """Send data to the WebSocket server"""
        if self.ws:
            try:
                self.ws.send(json.dumps(payload))
                print(f"sent: {payload}")
            except Exception as e:
                print(f"Failed to send: {e}")
        else:
            print("WebSocket not connected.")

    def close_connection(self):
        """Close the WebSocket connection gracefully"""
        if self.ws:
            self.ws.close()
            print("Connection closed.")
        else:
            print("WebSocket not connected.")

if __name__ == "__main__":
    # Create the WebSocket client instance
    server_client = RobotWebSocketClient(id="server", server_url="wss://b-e-m-o.onrender.com/api/ws/")
    
    # Start the WebSocket connection
    server_client.start_connection()

    while True:
        # Example: Press Enter to send status update
        x = input("Press Enter to send status... ")
        server_client.send_data({
            "robot_id": "bemo-MK1",
            "message": "Hello from the server!",
        })