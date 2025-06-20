# =========================
# Imports
# =========================
from utilities import BaseMQTTHandler
from utilities import (
    ERROR_RESPONSES,
    AUTH_RESPONSES,
    NO_FACE_RESPONSES,
    NO_FACE_RESPONSES_FINAL,
    BAD_FACE_RESPONSES,
    BAD_FACE_RESPONSES_FINAL,
    BLOCKED_RESPONSES,
)
import logging
import os
import random
import time

# =========================
# Constants
# =========================
DEFAULT_PATH = os.path.dirname(__file__)
AUTH_TASKS = []  # ! For testing
NAME = "main"
SUB_TOPIC = "main/main"
MAX_NO_FACE = 5
MAX_BAD_FACE = 3
BLOCK_TIME_RANGE = 15 * 60  # 15 minutes

# =========================
# Logging Setup
# =========================
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


# =========================
# Utility Functions
# =========================
blocked_ids = {}


def block_id(id: str):
    """
    Blocks the given id for a specified time range.
    """
    global blocked_ids
    if id in blocked_ids:
        print(f"ID {id} is already blocked.")
        return
    blocked_ids[id] = time.time()
    print(f"ID {id} is now blocked at {time.ctime(blocked_ids[id])}.")


def check_is_blocked(id: str) -> bool:
    """
    Checks if the given id is blocked and returns a boolean value.
    """
    current_time = time.time()
    if id in blocked_ids:
        block_time = blocked_ids[id]
        if current_time - block_time <= BLOCK_TIME_RANGE:
            print(f"ID {id} is still blocked.")
            return True
        else:
            del blocked_ids[id]
            print(f"ID {id} is no longer blocked.")
            return False
    else:
        print(f"ID {id} is not blocked. Proceeding normally.")
        return False


def clean_emotions(emotions: dict) -> dict:
    """
    Cleans the emotions dictionary by removing empty keys and values.
    """
    cleaned_emotions = {}
    for key, value in emotions.items():
        if key and value:
            cleaned_emotions[key] = value
    return cleaned_emotions


# =========================
# Main Handler Class
# =========================
class Main(BaseMQTTHandler):
    """
    Main handler for the server functionality.
    """

    def __init__(self):
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

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        """
        module_name = input_data.get("module_name")
        error = input_data.get("error", None)
        level = input_data.get("level", None)

        if not module_name:
            return self._handle_missing_module_name(input_data)

        logger.info(f"Module name: {module_name}")

        if error or self.error_dict:
            return self._handle_error(error, level)

        if module_name == "server":
            return self._handle_server_module(input_data)
        if module_name == "task_classifier":
            return self._handle_task_classifier_module(input_data)
        if module_name == "preprocessing":
            return self._handle_preprocessing_module(input_data)
        if module_name == "task_handler":
            return self._handle_task_handler_module(input_data)
        if module_name == "postprocessing":
            return self._handle_postprocessing_module(input_data)
        return None

    def _handle_missing_module_name(self, input_data: dict):
        self.error_dict = {
            "error": "Module name is missing, cannot identify the module",
            "level": 2,
        }
        logger.error("Module name is missing")
        robot_id = input_data.get("src_robot_id")
        if robot_id:
            self.robot_id = robot_id
            logger.info(f"Robot ID: {self.robot_id}")
            self.is_blocked = check_is_blocked(self.robot_id)
            if self.is_blocked:
                self.publish_result(
                    {
                        "is_error": False,
                        "response": random.choice(BLOCKED_RESPONSES),
                        "target_robot_id": self.robot_id,
                        "screen": "blocked",
                    },
                    topic="server/main",
                )
        else:
            logger.error("Robot ID is missing")
            return None
        return None

    def _handle_error(self, error, level):
        if error:
            self.error_dict = {"error": error, "level": level}
        logger.error(f"Error: {self.error_dict}")
        if self.error_dict["level"] == 4:
            self.publish_result(
                {
                    "is_error": True,
                    "response": random.choice(ERROR_RESPONSES),
                    "target_robot_id": self.robot_id,
                    "screen": "error",
                },
                topic="server/main",
            )
            self.end_time = time.time()
            logger.info(
                f"Execution time (All): {self.end_time - self.start_time} seconds"
            )
        else:
            self.publish_result(self.error_dict, topic="postprocessing/data")
        self.error_dict = {}
        return None

    def _handle_server_module(self, input_data: dict):
        self.start_time = time.time()
        logger.info("Received server module data")
        message = input_data.get("message")
        if not message:
            self.error_dict = {
                "error": "Prompt is missing from the server",
                "level": 2,
            }
            self.publish_result(self.error_dict, topic="postprocessing/data")
            logger.error("Prompt is missing")
            return None
        message = " ".join(message.split())
        if message in [":|", ":)", ":("]:
            return self._handle_face_message(message)
        else:
            return self._handle_prompt_message(input_data, message)

    def _handle_face_message(self, message: str):
        if message == ":)":
            logger.info("Face detected")
            self.publish_result(
                {
                    "predicted_labels": self.predicted_labels,
                    "split_prompts": self.split_prompts,
                },
                topic="preprocessing/data",
            )
            self.publish_result(
                {
                    "is_error": False,
                    "target_robot_id": self.robot_id,
                    "screen": "good_face",
                },
                topic="server/main",
            )
            self.no_face_counter = 0
            self.bad_face_counter = 0
            self.need_auth = False
        elif message == ":|":
            logger.info("No face detected")
            if self.no_face_counter >= MAX_NO_FACE:
                self.no_face_counter = 0
                self.bad_face_counter = 0
                self.need_auth = False
                self.publish_result(
                    {
                        "is_error": False,
                        "target_robot_id": self.robot_id,
                        "response": random.choice(NO_FACE_RESPONSES_FINAL),
                        "screen": "error",
                    },
                    topic="server/main",
                )
            else:
                self.no_face_counter += 1
                self.need_auth = True
                self.publish_result(
                    {
                        "is_error": False,
                        "is_auth": self.need_auth,
                        "target_robot_id": self.robot_id,
                        "response": random.choice(NO_FACE_RESPONSES),
                        "screen": "no_face",
                    },
                    topic="server/main",
                )
        else:
            logger.info("Bad face detected")
            if self.bad_face_counter >= MAX_BAD_FACE:
                block_id(self.robot_id)
                self.is_blocked = check_is_blocked(self.robot_id)
                self.need_auth = False
                self.publish_result(
                    {
                        "is_error": False,
                        "target_robot_id": self.robot_id,
                        "response": random.choice(BAD_FACE_RESPONSES_FINAL),
                        "screen": "blocked",
                    },
                    topic="server/main",
                )
                self.bad_face_counter = 0
                self.no_face_counter = 0
            else:
                self.bad_face_counter += 1
                self.need_auth = True
                self.publish_result(
                    {
                        "is_error": False,
                        "is_auth": self.need_auth,
                        "target_robot_id": self.robot_id,
                        "response": random.choice(BAD_FACE_RESPONSES),
                        "screen": "bad_face",
                    },
                    topic="server/main",
                )
        return None

    def _handle_prompt_message(self, input_data: dict, message: str):
        robot_id = input_data.get("src_robot_id")
        emotions = {
            input_data.get("top_label"): input_data.get("top_label_prob"),
            input_data.get("second_top_label"): input_data.get("second_top_label_prob"),
            input_data.get("Third_top_label"): input_data.get("Third_top_label_prob"),
        }
        if not robot_id:
            logger.error("Robot ID is missing")
            return None
        self.emotions = clean_emotions(emotions)
        self.prompt = message
        self.robot_id = robot_id
        logger.info(f"Received prompt: {self.prompt}")
        logger.info(f"Emotions: {self.emotions}")
        logger.info(f"Robot ID: {self.robot_id}")
        self.is_blocked = check_is_blocked(self.robot_id)
        if self.is_blocked:
            self.publish_result(
                {
                    "is_error": False,
                    "response": random.choice(BLOCKED_RESPONSES),
                    "target_robot_id": self.robot_id,
                    "screen": "blocked",
                },
                topic="server/main",
            )
        else:
            self.publish_result({"prompt": self.prompt}, topic="task_classifier/prompt")
        return None

    def _handle_task_classifier_module(self, input_data: dict):
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
            self.publish_result(
                {
                    "predicted_labels": self.predicted_labels,
                    "split_prompts": self.split_prompts,
                },
                topic="preprocessing/data",
            )
        else:
            logger.info(f"Authentication required for label: {auth_label}")
            self.publish_result(
                {
                    "is_error": False,
                    "is_auth": self.need_auth,
                    "target_robot_id": self.robot_id,
                    "response": random.choice(AUTH_RESPONSES),
                    "screen": "auth",
                },
                topic="server/main",
            )
        return None

    def _handle_preprocessing_module(self, input_data: dict):
        logger.info("Received preprocessing module data")
        logger.info(f"Preprocessed data: {input_data}")
        self.preprocessed_data = [input_data]
        task_name = input_data.get("method")
        if not task_name:
            self.error_dict = {
                "error": "Method is missing from the preprocessing module",
                "level": 2,
            }
            self.publish_result(self.error_dict, topic="postprocessing/data")
            logger.error("Method is missing")
            return None
        logger.info(f"Task name received from preprocessing: {task_name}")
        if task_name == "others":
            return self._handle_preprocessing_others(input_data)
        else:
            self.publish_result(
                {"preprocessed_data": self.preprocessed_data},
                topic="task_handler/main",
            )
        return None

    def _handle_preprocessing_others(self, input_data: dict):
        self.response = input_data.get("response")
        self.robot_emotion = input_data.get("robot_emotion", "neutral")
        self.robot_emotion = self.robot_emotion.lower()
        if not self.response:
            self.publish_result(
                {
                    "is_error": True,
                    "response": random.choice(ERROR_RESPONSES),
                    "target_robot_id": self.robot_id,
                    "screen": "error",
                },
                topic="server/main",
            )
            self.end_time = time.time()
            logger.info(
                f"Execution time (All): {self.end_time - self.start_time} seconds"
            )
            logger.error("Response is missing in the others method")
            return None
        logger.info("Returning the others method result to the server")
        logger.info(f"Response: {self.response}")
        logger.info(f"Robot emotion: {self.robot_emotion}")
        self.publish_result(
            {
                "status": "success",
                "response": self.response,
                "target_robot_id": self.robot_id,
                "screen": self.robot_emotion,
            },
            topic="server/main",
        )
        self.end_time = time.time()
        logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
        return None

    def _handle_task_handler_module(self, input_data: dict):
        logger.info("Received task_handler module data")
        self.task_results = input_data.get("results")
        if not self.task_results:
            self.error_dict = {
                "error": "Task results are missing from the task_handler module",
                "level": 2,
            }
            self.publish_result(self.error_dict, topic="postprocessing/data")
            logger.error("Task results are missing")
            return None
        logger.info(f"Task results: {self.task_results}")
        task_name = self.task_results.get("module_name")
        logger.info(f"Task name received from task_handler: {task_name}")
        self.publish_result(
            {
                "results": self.task_results,
                "prompt": self.prompt,
                "emotions": self.emotions,
            },
            topic="postprocessing/data",
        )
        return None

    def _handle_postprocessing_module(self, input_data: dict):
        logger.info("Received preprocessing module data")
        self.response = input_data.get("response")
        self.robot_emotion = input_data.get("robot_emotion", "neutral")
        self.robot_emotion = self.robot_emotion.lower()
        is_error = input_data.get("is_error")
        if not self.response:
            self.publish_result(
                {
                    "is_error": True,
                    "response": random.choice(ERROR_RESPONSES),
                    "target_robot_id": self.robot_id,
                    "screen": "error",
                },
                topic="server/main",
            )
            self.end_time = time.time()
            logger.info(
                f"Execution time (All): {self.end_time - self.start_time} seconds"
            )
            logger.error("Response is missing in the preprocessing method")
            return None
        logger.info("Returning the preprocessing method result to the server")
        logger.info(f"Response: {self.response}")
        logger.info(f"Robot emotion: {self.robot_emotion}")
        logger.info(f"Is error: {is_error}")
        if is_error:
            self.publish_result(
                {
                    "is_error": is_error,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": "error",
                },
                topic="server/main",
            )
        else:
            self.publish_result(
                {
                    "is_error": is_error,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                },
                topic="server/main",
            )
        self.end_time = time.time()
        logger.info(f"Execution time (All): {self.end_time - self.start_time} seconds")
        return None


# =========================
# Script Entry Point
# =========================
if __name__ == "__main__":
    main = Main()
    main.start_mqtt()
