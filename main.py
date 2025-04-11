import sys
from pathlib import Path

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utilities import BaseMQTTHandler

# Define the name of the module and the topics
NAME = "main"
SUB_TOPIC = "main/main"

class Server(BaseMQTTHandler):
    """
    Server is a class for handling the main server functionality.
    """
    
    def __init__(self):
        """
        Initialize the Server object.
        """
        
        # Initialize the BaseMQTTHandler object
        super().__init__(SUB_TOPIC, NAME)
        
    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        
        Args:
            input_data (dict): The input data to process.
        
        Returns:
            dict: The result of the classification.
        """
        # Process the input data
        result = {
            "status": "success",
            "message": "Data processed successfully",
            "data": input_data
        }
        
        # Return the result
        return result