import sys
from pathlib import Path
from utilities import BaseMQTTHandler, ERROR_RESPONSES
import logging
import os
import random
import time

DEFAULT_PATH = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

random.seed(time.time())

# Define the name of the module and the topics
NAME = "main"
SUB_TOPIC = "main/main"

# Todo: Add authentication
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
        self.split_prompts = []
        self.preprocessed_data = []
        self.response = ""
        self.task_results = {}
        self.error_dict = {}
        self.start_time = 0 
        self.end_time = 0
    
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
        
        error = input_data.get("error", None)
        level = input_data.get("level", None)
        
        if not module_name:
            self.error_dict = {"error": "Module name is missing, cannot identify the module", "level": 2}
            logger.error("Module name is missing")
            robot_id = input_data.get("src_robot_id")
            if robot_id:
                self.robot_id = robot_id
                logger.info(f"Robot ID: {self.robot_id}")
            else:
                logger.error("Robot ID is missing")
                return None
        else:
            logger.info(f"Module name: {module_name}")
        
        if error or self.error_dict:
            if error:
                self.error_dict = {"error": error, "level": level}
            
            logger.error(f"Error: {self.error_dict}")

            if self.error_dict["level"] == 4:
                self.publish_result({"is_error": True, "response": random.choice(ERROR_RESPONSES), "target_robot_id": self.robot_id}, topic="server/main")
                self.end_time = time.time()
                logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
            else:
                self.publish_result(self.error_dict, topic="postprocessing/data")
            
            self.error_dict = {}
            
            return None
            
        # Handle the case where module_name is "server"
        if module_name == "server":
            self.start_time = time.time()
            logger.info("Received server module data")
            prompt = input_data.get("message")
            robot_id = input_data.get("src_robot_id")
            emotions = {
                input_data.get("top_label"): input_data.get("top_label_prob"),
                input_data.get("second_top_label"): input_data.get("second_top_label_prob"),
                input_data.get("Third_top_label"): input_data.get("Third_top_label_prob")
            }
            if not prompt:
                self.error_dict = {"error": "Prompt is missing from the server", "level": 2}
                self.publish_result(self.error_dict, topic="postprocessing/data")
                logger.error("Prompt is missing")
                return None
            if not robot_id:
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
        # Todo: Handle llm
        # [global_publisher] Received message: {'predicted_labels': ['learning_resources'], 'split_prompts': ['Provide me with learning resources for Deep Learning, including courses and books.'], 'module_name': 'task_classifier'}
        if module_name == "task_classifier":
            logger.info("Received task_classifier module data")
            
            predicted_labels = input_data.get("predicted_labels")
            split_prompts = input_data.get("split_prompts")
            
            if not split_prompts:
                self.predicted_labels = predicted_labels
                logger.info(f"Predicted labels: {predicted_labels}")
                self.publish_result({"prompt": self.prompt, "predicted_labels": self.predicted_labels}, topic="preprocessing/data")
            else:
                self.split_prompts = split_prompts
                self.predicted_labels = predicted_labels
                logger.info(f"Predicted labels: {predicted_labels}")
                logger.info(f"Split prompts: {split_prompts}")
                self.publish_result({"prompt": self.prompt, "predicted_labels": self.predicted_labels, "split_prompts": self.split_prompts}, topic="preprocessing/data")
                    
            
            
        if module_name == "preprocessing":
            logger.info("Received preprocessing module data")
            logger.info(f"Preprocessed data: {input_data}")
            self.preprocessed_data = [input_data]

            task_name = input_data.get("method")
            if not task_name:
                self.error_dict = {"error": "Method is missing from the preprocessing module", "level": 2}
                self.publish_result(self.error_dict, topic="postprocessing/data")
                logger.error("Method is missing")
                return None

            logger.info(f"Task name received from preprocessing: {task_name}")

            if task_name == "others":
                self.response = input_data.get("response")
                if not self.response:
                    self.publish_result({"is_error": True, "response": random.choice(ERROR_RESPONSES), "target_robot_id": self.robot_id}, topic="server/main")
                    self.end_time = time.time()
                    logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
                    logger.error("Response is missing in the others method")
                    return None
                
                logger.info("Returning the others method result to the server")
                logger.info(f"Response: {self.response}")
                self.publish_result({"status": "success", "response": self.response, "target_robot_id": self.robot_id}, topic="server/main")
                self.end_time = time.time()
                logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")

                        
            else:
                self.publish_result({"preprocessed_data": self.preprocessed_data}, topic="task_handler/main")            
        
        # Handle the case where module_name is "task_handler"
        if module_name == "task_handler":
            logger.info("Received task_handler module data")
            self.task_results = input_data.get("results")
            if not self.task_results:
                self.error_dict = {"error": "Task results are missing from the task_handler module", "level": 2}
                self.publish_result(self.error_dict, topic="postprocessing/data")
                logger.error("Task results are missing")
                return None
            logger.info(f"Task results: {self.task_results}")
                                    
            task_name = self.task_results.get("module_name")
            logger.info(f"Task name received from task_handler: {task_name}")
            
            self.publish_result({"results": self.task_results, "prompt": self.prompt, "emotions": self.emotions}, topic="postprocessing/data")

        # Handle the case where module_name is "postprocessing"
        if module_name == "postprocessing":
            logger.info("Received preprocessing module data")
            self.response = input_data.get("output")
            is_error = input_data.get("is_error")
            if not self.response:
                self.publish_result({"is_error": True, "response": random.choice(ERROR_RESPONSES), "target_robot_id": self.robot_id}, topic="server/main")
                self.end_time = time.time()
                logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
                logger.error("Response is missing in the preprocessing method")
                return None
            logger.info("Returning the preprocessing method result to the server")
            logger.info(f"Response: {self.response}")
            self.publish_result({"is_error": is_error, "response": self.response, "target_robot_id": self.robot_id}, topic="server/main")
            self.end_time = time.time()
            logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")

            
        # Todo: DB
        
        return None
    
if __name__ == "__main__":
    main = Main()
    main.start_mqtt()