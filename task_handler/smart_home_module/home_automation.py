import os
import tinytuya
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utils import BaseMQTTHandler

DEFAULT_PATH = os.path.dirname(__file__)
# Cloud API credentials
API_REGION = os.getenv("API_REGION")
ACCESS_ID = os.getenv("ACCESS_ID")
ACCESS_KEY = os.getenv("ACCESS_KEY")
DEVICE_ID = os.getenv("DEVICE_ID")

class SmartHomeAutomation(BaseMQTTHandler):
    """
    SmartHomeAutomation class for handling smart home device control via MQTT and Tuya Cloud API.
    """

    def __init__(self):
        """
        Initialize the SmartHomeAutomation object.
        """
        # Load environment variables
        load_dotenv()
        self.API_REGION = os.getenv("API_REGION")
        self.ACCESS_ID = os.getenv("ACCESS_ID")
        self.ACCESS_KEY = os.getenv("ACCESS_KEY")
        self.DEVICE_ID = os.getenv("DEVICE_ID")

        # Initialize Tuya Cloud
        self.cloud = tinytuya.Cloud(
            apiRegion=self.API_REGION, apiKey=self.ACCESS_ID, apiSecret=self.ACCESS_KEY, apiDeviceID=self.DEVICE_ID
        )

        # Initialize BaseMQTTHandler with MQTT topics
        super().__init__(sub_topic="task_handler/smart_home", name="smart_home")
        self.__pub_topic = "task_handler/global"
        

    def control_device(self, switch_id, status):
        """
        Control a specific switch on the smart socket via the Tuya Cloud API.

        Parameters:
        switch_id (str): The switch identifier (e.g., 'switch_1', 'switch_2', 'switch_3').
        status (str): The status to set ('on' or 'off').

        Returns:
        bool: True if the command was successful, False otherwise.
        """
        try:
            result = self.cloud.sendcommand(
                self.DEVICE_ID, {"commands": [{"code": switch_id, "value": status == "on"}]}
            )
            return result.get("success", False)
        except Exception as e:
            print(f"Error controlling device: {e}")
            return False

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the smart home operation.
        """
        switches = input_data.get("switch", [])
        statuses = input_data.get("status", [])

        if not isinstance(switches, list) or not isinstance(statuses, list):
            switches = [switches]
            statuses = [statuses]

        results = []
        for switch, status in zip(switches, statuses):
            success = self.control_device(switch, status)
            results.append({"switch": switch, "status": status, "success": success})

        return {
            "method": "smart_home",
            "results": results
        }

if __name__ == "__main__":
    # Example usage
    smart_home = SmartHomeAutomation()
    smart_home.start() 