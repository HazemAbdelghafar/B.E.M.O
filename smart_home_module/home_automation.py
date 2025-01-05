import os
import tinytuya
from dotenv import load_dotenv

class SmartHomeAutomation:
    def __init__(self):
        load_dotenv()
        self.API_REGION = os.getenv("API_REGION")
        self.ACCESS_ID = os.getenv("ACCESS_ID")
        self.ACCESS_KEY = os.getenv("ACCESS_KEY")
        self.DEVICE_ID = os.getenv("DEVICE_ID")

        self.cloud = tinytuya.Cloud(
            apiRegion=self.API_REGION, apiKey=self.ACCESS_ID, apiSecret=self.ACCESS_KEY, apiDeviceID=self.DEVICE_ID
        )
        
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
            return False

    def execute_switch_control(self, smart_home):
        """
        Parse the user command to identify switches and their status.

        Parameters:
        command (str): The user's input command.

        Returns:
        list or None: A list of (switch, status) tuples or None if parsing fails.
        """


        if not isinstance(smart_home["switch"], list) or not isinstance(smart_home["status"], list):
            try:
                self.control_device(smart_home["switch"], smart_home["status"])
            except:
                return False
        else:
            for i in range(len(smart_home["switch"])):
                try:
                    self.control_device(smart_home["switch"][i], smart_home["status"][i])
                except:
                    return False
        return True

if __name__ == "__main__":
    smart_home = {
        "switch": ["switch_1", "switch_2", "switch_3"],
        "status": ["off", "off", "on"]
    }
    smart_home_automation = SmartHomeAutomation()
    result = smart_home_automation.execute_switch_control(smart_home=smart_home)
    print(result)