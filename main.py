
import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import BaseMQTTHandler

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