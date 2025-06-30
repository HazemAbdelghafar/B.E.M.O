from websocket import WebSocketApp, WebSocket
import json
import threading
import time
import sys
from pathlib import Path
from ast import literal_eval

import os
from dotenv import find_dotenv, dotenv_values
import logging

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utilities import BaseMQTTHandler

DEFAULT_PATH = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="./logging.log",
    encoding="utf-8",
    level=logging.DEBUG,
)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


class ServerWebSocketClient(BaseMQTTHandler):
    """ServerWebSocketClient is a class for handling WebSocket communication with a server."""

    def __init__(self, max_retries: int = 3, retry_interval: int = 10):
        """
        Initialize the WebSocket server.

        Args:
            max_retries (int): Maximum number of connection retries.
            retry_interval (int): Interval (in seconds) between connection retries.
        """
        super().__init__(sub_topic="server/main", name="server")

        self.id = dotenv_values(find_dotenv())["SERVER_ID"]
        self.server_url = dotenv_values(find_dotenv())["URL"] + self.id
        self.ws = None
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.retry_count = 0

    def on_open(self, socket: WebSocket):
        self.ws = socket
        self.end_time = time.time()
        logger.info(
            f"Connected to forwarding server in {self.end_time - self.start_time} seconds"
        )

    def on_message(self, socket: WebSocket, message: str):
        """
        Callback function that is called when a message is received from a WebSocket client.

        Args:
            socket (WebSocket): The WebSocket object representing the client connection.
            message (str): The message received from the client.
        """
        thread = threading.Thread(target=self.process_message, args=(message,))
        thread.start()

    def on_error(self, socket: WebSocket, error: str):
        logger.error(f"Error: {error}")

    def on_close(self, socket: WebSocket, close_status_code: int, close_msg: str):
        logger.warning(f"Connection closed")
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            logger.warning(
                f"Attempting to reconnect ({self.retry_count}/{self.max_retries})..."
            )
            time.sleep(self.retry_interval)
            self.start_connection()
        else:
            logger.error("Max retries reached. Connection failed permanently.")

    def start_connection(self):
        """
        Starts the WebSocket connection to the server.
        """
        ws = WebSocketApp(
            self.server_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        thread = threading.Thread(
            target=lambda: ws.run_forever(ping_interval=10, ping_timeout=5)
        )
        thread.daemon = True
        thread.start()
        self.start_time = time.time()
        time.sleep(1)

    def send_data(self, payload: dict):
        """
        Sends the provided payload as a JSON string over the WebSocket connection.

        Args:
            payload (dict): The data to be sent.

        Raises:
            Exception: If there is an error while sending the data.

        """
        if self.ws:
            try:
                self.ws.send(json.dumps(payload))
                logger.info(f"Sent: {payload}")
            except Exception as e:
                logger.error(f"Failed to send: {e}")
        else:
            logger.error("WebSocket not connected.")

    def close_connection(self):
        """
        Closes the WebSocket connection.

        If the WebSocket connection is open, it will be closed. Otherwise, an error message will be logged.

        """
        if self.ws:
            self.ws.close()
            logger.info("Connection closed.")
        else:
            logger.error("WebSocket not connected.")

    def process_message(self, message: str):
        """
        Process the received message.
        This function is run in a separate thread to handle incoming messages.
        Args:
            message (str): The message to process.
        """
        thread_name = threading.current_thread().name

        logger.info(f"[{thread_name}] Received message: {message}")

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            try:
                data = literal_eval(message)
            except Exception as e:
                logger.error(f"Invalid JSON format: {e}")
                return

        self.publish_result(data)  # Publish the result to the MQTT broker

        logger.info(f"[{thread_name}] Published message: {data}")

    def execute_main(self, input_data: dict):
        """
        Execute the main function of the class.
        This method should be overridden by child classes.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the main function.
        """
        self.send_data(input_data)
        return None


if __name__ == "__main__":
    server_client = ServerWebSocketClient()
    server_client.start_connection()
    server_client.start_mqtt()
