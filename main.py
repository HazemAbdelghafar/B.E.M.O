from utilities import BaseMQTTHandler
from utilities import ERROR_RESPONSES, AUTH_RESPONSES, NO_FACE_RESPONSES, NO_FACE_RESPONSES_FINAL, BAD_FACE_RESPONSES, BAD_FACE_RESPONSES_FINAL, BLOCKED_RESPONSES
import logging
import os
import random
import time

DEFAULT_PATH = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

AUTH_TASKS = ["todo", "mail"]

# Define the name of the module and the topics
NAME = "main"
SUB_TOPIC = "main/main"

MAX_NO_FACE = 5
MAX_BAD_FACE = 3
BLOCK_TIME_RANGE = 15 * 60  # 15 minutes

blocked_ids = {}

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
        self.robot_emotion = "neutral"
        self.task_results = {}
        self.error_dict = {}
        self.start_time = 0 
        self.end_time = 0
        self.need_auth = False
        self.no_face_counter = 0
        self.bad_face_counter = 0
        self.is_blocked = False
        
        random.seed(time.time())
    
    def block_id(self, id: str):
        """
        Blocks the given id for a specified time range.
        
        Args:
            id (str): The id to block.
        """
        global blocked_ids
        
        # Check if the id is already blocked
        if id in blocked_ids:
            print(f"ID {id} is already blocked.")
            return        

        blocked_ids[id] = time.time()
        print(f"ID {id} is now blocked at {time.ctime(blocked_ids[id])}.")

    def check_is_blocked(self, id: str) -> bool:
        """
        Checks if the given id is blocked and returns a boolean value.
        
        Args:
            id (str): The id to check.
            
        Returns:
            bool: True if the id is blocked, False otherwise.
        """
        # Get the current time
        current_time = time.time()

        # Check if the id is in the blocked_ids dictionary
        if id in blocked_ids:
            # Check if the time difference is within the block time range
            block_time = blocked_ids[id]
            if current_time - block_time <= BLOCK_TIME_RANGE:
                # If within the block time range, return a custom message
                print(f"ID {id} is still blocked.")
                return True
            else:
                # If outside the block time range, unblock the id
                del blocked_ids[id]
                print(f"ID {id} is no longer blocked.")
                return False
        else:
            # If the id is not blocked, return a normal response
            print(f"ID {id} is not blocked. Proceeding normally.")
            return False

    
    def clean_emotions(self, emotions: dict) -> dict:
        """
        Cleans the emotions dictionary by removing empty keys and values.
        
        Args:
            emotions (dict): The emotions dictionary to clean.
            
        Returns:
            dict: The cleaned emotions dictionary.
        """
        cleaned_emotions = {}
        for key, value in emotions.items():
            if key and value:
                cleaned_emotions[key] = value
                
        return cleaned_emotions
    
    # Todo: Clean the code and remove unnecessary comments
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
                self.is_blocked = self.check_is_blocked(self.robot_id)
                if self.is_blocked:
                    self.publish_result({"is_error": False, "response": random.choice(BLOCKED_RESPONSES), "target_robot_id": self.robot_id, "screen": "blocked"}, topic="server/main")
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
                self.publish_result({"is_error": True, "response": random.choice(ERROR_RESPONSES), "target_robot_id": self.robot_id, "screen": "error"}, topic="server/main")
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
            message = input_data.get("message")
            if not message:
                self.error_dict = {"error": "Prompt is missing from the server", "level": 2}
                self.publish_result(self.error_dict, topic="postprocessing/data")
                logger.error("Prompt is missing")
                return None
            
            # Remove extra spaces from the message
            message = " ".join(message.split())
            
            if message in [":|", ":)", ":("]:
                if message == ":)":
                    logger.info("Face detected")
                    self.publish_result({"predicted_labels": self.predicted_labels, "split_prompts": self.split_prompts}, topic="preprocessing/data")
                    self.no_face_counter = 0
                    self.bad_face_counter = 0
                    self.need_auth = False
                elif message == ":|":
                    logger.info("No face detected")
                    if self.no_face_counter >= MAX_NO_FACE:
                        self.no_face_counter = 0
                        self.bad_face_counter = 0
                        self.need_auth = False
                        self.publish_result({"is_error": False, "target_robot_id": self.robot_id, "response": random.choice(NO_FACE_RESPONSES_FINAL), "screen": "error"}, topic="server/main")
                    else:
                        self.no_face_counter += 1
                        self.need_auth = True
                        self.publish_result({"is_error": False, "is_auth": self.need_auth, "target_robot_id": self.robot_id, "response": random.choice(NO_FACE_RESPONSES), "screen": "no_face"}, topic="server/main")
                else:
                    logger.info("Bad face detected")
                    if self.bad_face_counter >= MAX_BAD_FACE:
                        # Block the robot ID
                        self.block_id(self.robot_id)
                        self.is_blocked = self.check_is_blocked(self.robot_id)
                        self.need_auth = False
                        self.publish_result({"is_error": False, "target_robot_id": self.robot_id, "response": random.choice(BAD_FACE_RESPONSES_FINAL), "screen": "blocked"}, topic="server/main")
                        # TODO: Send email to check the robot
                        self.bad_face_counter = 0
                        self.no_face_counter = 0
                    else:
                        self.bad_face_counter += 1
                        self.need_auth = True
                        self.publish_result({"is_error": False, "is_auth": self.need_auth, "target_robot_id": self.robot_id, "response": random.choice(BAD_FACE_RESPONSES), "screen": "bad_face"}, topic="server/main")

            else:
                robot_id = input_data.get("src_robot_id")
                emotions = {
                    input_data.get("top_label"): input_data.get("top_label_prob"),
                    input_data.get("second_top_label"): input_data.get("second_top_label_prob"),
                    input_data.get("Third_top_label"): input_data.get("Third_top_label_prob")
                }
                if not robot_id:
                    logger.error("Robot ID is missing")
                    return None
            
                self.emotions = self.clean_emotions(emotions)
                self.prompt = message
                self.robot_id = robot_id
                
                logger.info(f"Received prompt: {self.prompt}")
                logger.info(f"Emotions: {self.emotions}")
                logger.info(f"Robot ID: {self.robot_id}")
                
                self.is_blocked = self.check_is_blocked(self.robot_id)
                if self.is_blocked:
                    self.publish_result({"is_error": False, "response": random.choice(BLOCKED_RESPONSES), "target_robot_id": self.robot_id, "screen": "blocked"}, topic="server/main")
                else:
                    self.publish_result({"prompt": self.prompt}, topic="task_classifier/prompt")
                
        # Handle the case where module_name is "task_classifier"
        if module_name == "task_classifier":
            logger.info("Received task_classifier module data")
            
            predicted_labels = input_data.get("predicted_labels")
            split_prompts = input_data.get("split_prompts")
            
            self.predicted_labels = predicted_labels
            logger.info(f"Predicted labels: {self.predicted_labels}")
            
            if not split_prompts:
                split_prompts = [self.prompt] * len(predicted_labels)
            
            self.split_prompts = split_prompts
            logger.info(f"Split prompts: {split_prompts}")
            
            auth_label = ""
            for label in self.predicted_labels:
                if label in AUTH_TASKS:
                    self.need_auth = True
                    auth_label = label
                else:
                    self.need_auth = False
                    
                
            if not self.need_auth:
                logger.info("No authentication required")                
                self.publish_result({"predicted_labels": self.predicted_labels, "split_prompts": self.split_prompts}, topic="preprocessing/data")
            else:
                logger.info(f"Authentication required for label: {auth_label}")
                self.publish_result({"is_error": False, "is_auth": self.need_auth, "target_robot_id": self.robot_id, "response": random.choice(AUTH_RESPONSES), "screen": "auth"}, topic="server/main")
               
                            
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
                self.robot_emotion = input_data.get("robot_emotion", "neutral")
                self.robot_emotion = self.robot_emotion.lower()
                if not self.response:
                    self.publish_result({"is_error": True, "response": random.choice(ERROR_RESPONSES), "target_robot_id": self.robot_id, "screen": "error"}, topic="server/main")
                    self.end_time = time.time()
                    logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
                    logger.error("Response is missing in the others method")
                    return None
                
                logger.info("Returning the others method result to the server")
                logger.info(f"Response: {self.response}")
                logger.info(f"Robot emotion: {self.robot_emotion}")
                self.publish_result({"status": "success", "response": self.response, "target_robot_id": self.robot_id, "screen": self.robot_emotion}, topic="server/main")
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
            self.response = input_data.get("response")
            self.robot_emotion = input_data.get("robot_emotion", "neutral")
            self.robot_emotion = self.robot_emotion.lower()
            
            is_error = input_data.get("is_error")
            
            if not self.response:
                self.publish_result({"is_error": True, "response": random.choice(ERROR_RESPONSES), "target_robot_id": self.robot_id, "screen": "error"}, topic="server/main")
                self.end_time = time.time()
                logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
                logger.error("Response is missing in the preprocessing method")
                return None
            
            logger.info("Returning the preprocessing method result to the server")
            logger.info(f"Response: {self.response}")
            logger.info(f"Robot emotion: {self.robot_emotion}")
            logger.info(f"Is error: {is_error}")
            
            if is_error:
                self.publish_result({"is_error": is_error, "response": self.response, "target_robot_id": self.robot_id, "screen": "error"}, topic="server/main")
            else:
                self.publish_result({"is_error": is_error, "response": self.response, "target_robot_id": self.robot_id, "screen": self.robot_emotion}, topic="server/main")

            self.end_time = time.time()
            logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")

        # Todo: DB
        
        return None
    
if __name__ == "__main__":
    main = Main()
    main.start_mqtt()