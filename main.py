import sys
from pathlib import Path
from utilities import BaseMQTTHandler
import logging
import os

DEFAULT_PATH = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

# Define the name of the module and the topics
NAME = "main"
SUB_TOPIC = "main/main"

# Todo: THREAAADDINGGG
class Main(BaseMQTTHandler):
    """
    Server is a class for handling the main server functionality.
    """
    
    def __init__(self):
        """
        Initialize the Server object.
        """
        
        # Initialize the BaseMQTTHandler object
        super().__init__(SUB_TOPIC, NAME)
        self.robot_id = ""
        self.emotions = {}
        self.prompt = ""
        self.predicted_labels = []
        self.preprocessed_data = []
        self.response = ""
    
    def clean_emotions(self, emotions: dict) -> dict:
        # If both the key and value are empty, remove the key from the dictionary
        cleaned_emotions = {}
        for key, value in emotions.items():
            if key and value:
                cleaned_emotions[key] = value
                
        return cleaned_emotions
        
    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        
        Args:
            input_data (dict): The input data to process.
        
        Returns:
            dict: The result of the classification.
        """
        module_name = input_data.get("module_name")
        error = input_data.get("error")
        logger.info(f"Module name: {module_name}")
        
        if error:
            # Todo: Handle the error case
            logger.error(f"Error in input data: {error}")
            pass
        
        if not module_name:
            # Todo: Handle the case where module_name is not provided
            logger.error("Module name is missing")
            pass
        
        # Handle the case where module_name is "server"
        if module_name == "server":
            logger.info("Received server module data")
            prompt = input_data.get("message")
            robot_id = input_data.get("src_robot_id")
            emotions = {
                input_data.get("top_label"): input_data.get("top_label_prob"),
                input_data.get("second_top_label"): input_data.get("second_top_label_prob"),
                input_data.get("Third_top_label"): input_data.get("Third_top_label_prob")
            }
            if not prompt:
                # Todo: Handle the case where prompt is not provided
                logger.error("Prompt is missing")
                return None
            if not robot_id:
                # Todo: Handle the case where robot_id is not provided
                logger.error("Robot ID is missing")
                return None
            
            self.emotions = self.clean_emotions(emotions)
            self.prompt = prompt
            self.robot_id = robot_id
            
            logger.info(f"Received prompt: {prompt}")
            logger.info(f"Emotions: {emotions}")
            logger.info(f"Robot ID: {robot_id}")
            
            self.publish_result({"prompt": self.prompt}, topic="task_classifier/prompt")
                
        # Handle the case where module_name is "task_classifier"
        if module_name == "task_classifier":
            logger.info("Received task_classifier module data")
            
            predicted_labels = input_data.get("predicted_labels")
            self.predicted_labels = predicted_labels
            logger.info(f"Predicted labels: {predicted_labels}")
            
            self.publish_result({"prompt": self.prompt, "predicted_labels": self.predicted_labels}, topic="preprocessing/data")
                
        if module_name == "preprocessing":
            logger.info("Received preprocessing module data")
            logger.info(f"Preprocessed data: {input_data}")
            self.preprocessed_data = [input_data]

            method = input_data.get("method")
            if not method:
                # Todo: Handle the case where the method is not sent back
                logger.error("Method is missing")
                return None

            logger.info(f"Method: {method}")

            if method == "others":
                self.response = input_data.get("response")
                if not self.response:
                    # Todo: Handle the case where the response is not sent back
                    logger.error("Response is missing in the others method")
                    return None
                
                logger.info("Returning the result to the server")
                logger.info(f"Response: {self.response}")
                self.publish_result({"status": "success", "response": self.response, "target_robot_id": self.robot_id}, topic="server/main")
            
            elif method == "learning_resource":
                self.response = input_data.get("model_output")
                if not self.response:
                    logger.error("Response is missing in the learning_resource method")
                    self.publish_result({"preprocessed_data": self.preprocessed_data}, topic="task_handler/main") 
                else:
                    logger.info("Returning the result to the server")
                    self.publish_result({"status": "success", "response": self.response, "target_robot_id": self.robot_id}, topic="server/main")
            
            else:
                self.publish_result({"preprocessed_data": self.preprocessed_data}, topic="task_handler/main")            
         
        if module_name == "task_handler":
            logger.info("Received task_handler module data")
            logger.info(f"Task handler data: {input_data}")
            
        # Todo: DB
        # Todo: Post-process the data
        
        # Return the result
        return None
    
if __name__ == "__main__":
    main = Main()
    main.start_mqtt()