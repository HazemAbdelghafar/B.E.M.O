import os
import tinytuya
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cloud API credentials
API_REGION = os.getenv('API_REGION')
ACCESS_ID = os.getenv('ACCESS_ID')
ACCESS_KEY = os.getenv('ACCESS_KEY')
DEVICE_ID = os.getenv('DEVICE_ID')

print(API_REGION, ACCESS_ID, ACCESS_KEY, DEVICE_ID)

# Initialize Tuya Cloud
cloud = tinytuya.Cloud(
    apiRegion=API_REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_KEY,
    apiDeviceID=DEVICE_ID
)

def control_device(switch, action):
    """
    Control a specific switch on the smart socket via the Tuya Cloud API.

    Parameters:
    switch (str): The switch identifier (e.g., 'switch_1', 'switch_2', 'switch_3').
    action (str): The action to perform ('on' or 'off').

    Returns:
    None
    """
    print(f"Control device called with switch: {switch}, action: {action}")
    try:
        if action == 'on':
            result = cloud.sendcommand(DEVICE_ID, {'commands': [{'code': switch, 'value': True}]})
            print(f"Turned on {switch} via cloud. Result: {result}")
        elif action == 'off':
            result = cloud.sendcommand(DEVICE_ID, {'commands': [{'code': switch, 'value': False}]})
            print(f"Turned off {switch} via cloud. Result: {result}")
        else:
            print("Invalid action.")
    except Exception as e:
        print(f"Cloud control failed: {e}")

def main(swithc, status):
    """
    Main function to handle user input and control the smart socket switches.

    This function runs an infinite loop, taking commands from the user via the terminal
    and controlling the smart socket switches accordingly. The loop can be exited by
    entering the 'exit' command.

    Returns:
    None
    """
    while True:
        command = input("Enter command: ").lower().strip()
        print(f"Received command: {command}")  # Debug print
        if command:
            if command == 'switch one on':
                control_device('switch_1', 'on')
            elif command == 'switch one off':
                control_device('switch_1', 'off')
            elif command == 'switch two on':
                control_device('switch_2', 'on')
            elif command == 'switch two off':
                control_device('switch_2', 'off')
            elif command == 'switch three on':
                control_device('switch_3', 'on')
            elif command == 'switch three off':
                control_device('switch_3', 'off')
            elif command == 'exit':
                print("Exiting...")
                break
            else:
                print("Invalid command.")

if __name__ == "__main__":
    main()