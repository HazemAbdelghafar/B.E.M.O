import sys
from pathlib import Path

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utilities import BaseMQTTHandler

# Define the name of the module and the topics
NAME = "server"
SUB_TOPIC = "server/main"

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
    
    def authenticatiom(self, input_data: dict) -> dict:
        """
        # TODO
        Authenticate the input data.
        
        """
        return input_data