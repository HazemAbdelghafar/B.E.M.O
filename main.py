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
# AUTH_TASKS = ["todo", "mail"]
# AUTH_TASKS = ["mail"]
AUTH_TASKS = []  # ! For testing
NAME = "main"
SUB_TOPIC = "main/main"
MAX_NO_FACE = 3
MAX_BAD_FACE = 2
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
# Global Variables
# =========================
blocked_ids = {}

# robot_id -> user_id
robot_user_mapping = {}

# ! For testing
DEFAULT_USER_MAPPING = {
    "bemo-MK0": "user-MK0",
    "bemo-MK1": "user-MK1",
    "bemo-MK2": "user-MK2",
    "bemo-MK3": "user-MK3",
    "bemo-MK4": "user-MK4",
    "bemo-MK5": "user-MK5",
}

# =========================
# Utility Functions
# =========================


def get_user_id(robot_id: str) -> str:
    """
    Returns the user ID for the given robot ID.
    """
    global robot_user_mapping
    return robot_user_mapping.get(robot_id, DEFAULT_USER_MAPPING.get(robot_id))


def set_user_id(robot_id: str, user_id: str):
    """
    Sets the user ID for the given robot ID.
    """
    global robot_user_mapping
    robot_user_mapping[robot_id] = user_id
    logger.info(f"User ID set for robot ID {robot_id}: {user_id}")


def get_robot_id(user_id: str) -> str:
    """
    Returns the robot ID for the given user ID.
    """
    global robot_user_mapping
    for robot_id, user_id_ in robot_user_mapping.items():
        if user_id_ == user_id:
            return robot_id
    return None


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
        self.user_id = ""
        self.user_data = {}

        self.user_emotions = {}
        self.prompt = ""

        self.predicted_labels = []
        self.split_prompts = []

        self.preprocessed_data = []
        self.task_results = {}

        self.response = ""
        self.robot_emotion = "neutral"

        self.start_time = 0
        self.end_time = 0
        self.execution_time = 0

        self.empty_data_counter = 0

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

        logger.info(f"Module name: {module_name}")

        if not module_name or error:
            self._handle_error(input_data)
            return None

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
        if module_name == "user_data":
            return self._handle_user_data_module(input_data)

        # Todo: DB

        self._handle_error({"error": "Module name is not valid", "level": 2})
        return None

    def _handle_user_data_module(self, input_data: dict):
        logger.info("Received user_data module data")
        self.user_data = input_data.get("data")
        logger.info(f"User data: {self.user_data}")
        return None

    def _publish_to_app(self, is_error: bool):
        time.sleep(0.1)

        if not self.user_id:
            if not self.robot_id:
                logger.error("User ID and Robot ID are missing")
                return
            self.user_id = get_user_id(self.robot_id)
            if not self.user_id:
                logger.error("User ID is missing")
                return

        # Initialize counter if not already
        if not hasattr(self, "_predicted_counter"):
            self._predicted_counter = len(self.predicted_labels)

        # Safety check
        if self._predicted_counter <= 0:
            logger.warning("Predicted labels already sent completely.")
            return

        # Get the current message to send
        current_index = len(self.predicted_labels) - self._predicted_counter
        current_label = self.predicted_labels[current_index]
        current_prompt = self.split_prompts[current_index]

        logger.info(
            f"Publishing to app (part {current_index + 1}/{len(self.predicted_labels)}) "
            f"with user ID: {self.user_id}, and robot ID: {self.robot_id}"
        )

        self.publish_result(
            {
                "target_user_id": self.user_id,
                "prompt": self.prompt,
                "user_emotions": self.user_emotions,
                "predicted_labels": current_label,
                "split_prompts": current_prompt,
                "preprocessed_data": self.preprocessed_data,
                "task_results": self.task_results,
                "response": self.response,
                "robot_emotion": self.robot_emotion,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "execution_time": self.execution_time,
                "is_error": is_error,
            },
            topic="server/main",
        )

        self._predicted_counter -= 1

        # Empty only after sending all items
        if self._predicted_counter == 0:
            del self._predicted_counter
            return self.empty_data()

        return None

    def empty_data(self):
        logger.info("Emptying data")

        self.prompt = ""
        self.user_emotions = {}

        self.predicted_labels = []
        self.split_prompts = []

        self.preprocessed_data = []
        self.task_results = {}

        self.response = ""
        self.robot_emotion = "neutral"

        self.start_time = 0
        self.end_time = 0
        self.execution_time = 0
        return None

    def _handle_error(self, input_data: dict):
        module_name = input_data.get("module_name", None)
        if not module_name:
            error_dict = {
                "error": "Module name is missing, cannot identify the module",
                "level": 2,
            }
            logger.error("Module name is missing")

        error = input_data.get("error", None)
        level = input_data.get("level", None)

        if error:
            error_dict = {"error": error, "level": level}
            logger.error(f"Error: {error_dict}")

        if error_dict["level"] == 4:
            if not self.robot_id:
                self.robot_id = input_data.get("src_robot_id", "")
            if not self.robot_id:
                logger.error("Robot ID is missing")
                return None
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.response = random.choice(ERROR_RESPONSES)
            self.robot_emotion = "error"
            self.publish_result(
                {
                    "is_error": True,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=True)
        else:
            self.publish_result(error_dict, topic="postprocessing/data")

        return None

    def _handle_server_module(self, input_data: dict):
        logger.info("Received server module data")
        data = input_data.get("data")
        if data:
            return self._handle_data(data)

        self.start_time = time.time()
        message = input_data.get("message")

        if message:
            message = " ".join(message.split())
            if message in [":|", ":)", ":("]:
                return self._handle_face_recognition(message)
            else:
                return self._handle_prompt_message(input_data, message)
        else:
            error_dict = {
                "error": "Message is missing from the server module",
                "level": 2,
            }
            self.publish_result(error_dict, topic="postprocessing/data")
            logger.error("Message is missing from the server module")
            return None

    def _handle_data(self, data: dict):
        user_id = data.get("src_user_id")
        if not user_id:
            logger.error("User ID is missing from the server module")
            return None

        robot_id = data.get("robot_id")
        if not robot_id:
            logger.error("Robot ID is missing from the server module")
            return None

        self.user_id = user_id
        self.robot_id = robot_id
        set_user_id(robot_id, user_id)
        logger.info(f"Robot ID: {self.robot_id}, User ID: {self.user_id}")

        keys = []
        values = []

        for key, value in data.items():
            keys.append(key)
            values.append(value)

        logger.info(f"Keys: {keys}")
        logger.info(f"Values: {values}")

        self.publish_result(
            {
                "action": "set",
                "robot_id": self.robot_id,
                "user_id": self.user_id,
                "keys": keys,
                "values": values,
            },
            topic="user_data/main",
        )
        time.sleep(0.1)
        self.publish_result(
            {
                "action": "get",
                "robot_id": self.robot_id,
                "user_id": self.user_id,
                "key": "all",
            },
            topic="user_data/main",
        )
        return None

    def _handle_face_recognition(self, message: str):
        if message == ":)":
            logger.info("Face detected")
            self.publish_result(
                {
                    "predicted_labels": self.predicted_labels,
                    "split_prompts": self.split_prompts,
                    "user_data": self.user_data,
                },
                topic="preprocessing/data",
            )
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.robot_emotion = "good_face"
            self.publish_result(
                {
                    "is_error": False,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
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

                self.end_time = time.time()
                self.execution_time = self.end_time - self.start_time
                self.response = random.choice(NO_FACE_RESPONSES_FINAL)
                self.robot_emotion = "error"
                self.publish_result(
                    {
                        "is_error": False,
                        "target_robot_id": self.robot_id,
                        "response": self.response,
                        "screen": self.robot_emotion,
                        "time_taken": self.execution_time,
                    },
                    topic="server/main",
                )
                self._publish_to_app(is_error=False)
            else:
                self.no_face_counter += 1
                self.need_auth = True
                self.end_time = time.time()
                self.execution_time = self.end_time - self.start_time
                self.response = random.choice(NO_FACE_RESPONSES)
                self.robot_emotion = "no_face"
                self.publish_result(
                    {
                        "is_error": False,
                        "is_auth": self.need_auth,
                        "target_robot_id": self.robot_id,
                        "response": self.response,
                        "screen": self.robot_emotion,
                        "time_taken": self.execution_time,
                    },
                    topic="server/main",
                )
                self._publish_to_app(is_error=False)
        else:
            logger.info("Bad face detected")
            if self.bad_face_counter >= MAX_BAD_FACE:
                block_id(self.robot_id)
                self.is_blocked = check_is_blocked(self.robot_id)
                self.need_auth = False

                self.end_time = time.time()
                self.execution_time = self.end_time - self.start_time
                self.response = random.choice(BAD_FACE_RESPONSES_FINAL)
                self.robot_emotion = "blocked"
                self.publish_result(
                    {
                        "is_error": False,
                        "target_robot_id": self.robot_id,
                        "response": self.response,
                        "screen": self.robot_emotion,
                        "time_taken": self.execution_time,
                    },
                    topic="server/main",
                )
                self._publish_to_app(is_error=False)

                self.publish_result(
                    {
                        "preprocessed_data": [
                            {
                                "method": "mail",
                                "function": "send_email",
                                "recipients": self.user_data.get("primary_email", ""),
                                "subject": "Check your robot for unusual activity",
                                "body": "This is an automated email from BeMo's system.\n\nA user has attempted to access sensitive features on your robot. Please check its status to ensure everything is working as expected and no unauthorized activity has occurred.\n\nRegards,\nBeMo's Team",
                                "module_name": "preprocessing",
                            }
                        ]
                    },
                    topic="task_handler/main",
                )
                self.bad_face_counter = 0
                self.no_face_counter = 0
            else:
                self.bad_face_counter += 1
                self.need_auth = True
                self.end_time = time.time()
                self.execution_time = self.end_time - self.start_time
                self.response = random.choice(BAD_FACE_RESPONSES)
                self.robot_emotion = "bad_face"
                self.publish_result(
                    {
                        "is_error": False,
                        "is_auth": self.need_auth,
                        "target_robot_id": self.robot_id,
                        "response": self.response,
                        "screen": self.robot_emotion,
                        "time_taken": self.execution_time,
                    },
                    topic="server/main",
                )
                self._publish_to_app(is_error=False)
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

        self.user_emotions = clean_emotions(emotions)
        self.prompt = message
        self.robot_id = robot_id
        logger.info(f"Received prompt: {self.prompt}")
        logger.info(f"Emotions: {self.user_emotions}")
        logger.info(f"Robot ID: {self.robot_id}")
        self.is_blocked = check_is_blocked(self.robot_id)
        if self.is_blocked:
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.response = random.choice(BLOCKED_RESPONSES)
            self.robot_emotion = "blocked"
            self.publish_result(
                {
                    "is_error": False,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=False)
        else:
            self.publish_result({"prompt": self.prompt}, topic="task_classifier/prompt")

        self.publish_result(
            {
                "action": "get",
                "robot_id": self.robot_id,
                "user_id": get_user_id(self.robot_id),
                "key": "all",
            },
            topic="user_data/main",
        )
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
                    "user_data": self.user_data,
                },
                topic="preprocessing/data",
            )
        else:
            logger.info(f"Authentication required for label: {auth_label}")
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.response = random.choice(AUTH_RESPONSES)
            self.robot_emotion = "auth"
            self.publish_result(
                {
                    "is_error": False,
                    "is_auth": self.need_auth,
                    "target_robot_id": self.robot_id,
                    "response": self.response,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=False)
        return None

    def _handle_preprocessing_module(self, input_data: dict):
        logger.info("Received preprocessing module data")
        logger.info(f"Preprocessed data: {input_data}")
        self.preprocessed_data = [input_data]
        task_name = input_data.get("method")
        if not task_name:
            error_dict = {
                "error": "Method is missing from the preprocessing module",
                "level": 2,
            }
            self.publish_result(error_dict, topic="postprocessing/data")
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
        self.task_results = self.response
        if not self.response:
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.response = random.choice(ERROR_RESPONSES)
            self.robot_emotion = "error"
            self.publish_result(
                {
                    "is_error": True,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=True)
            logger.error("Response is missing in the others method")
            return None
        logger.info("Returning the others method result to the server")
        logger.info(f"Response: {self.response}")
        logger.info(f"Robot emotion: {self.robot_emotion}")
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time
        self.publish_result(
            {
                "is_error": False,
                "response": self.response,
                "target_robot_id": self.robot_id,
                "screen": self.robot_emotion,
                "time_taken": self.execution_time,
            },
            topic="server/main",
        )
        self._publish_to_app(is_error=False)
        return None

    def _handle_task_handler_module(self, input_data: dict):
        logger.info("Received task_handler module data")
        self.task_results = input_data.get("results")
        if not self.task_results:
            error_dict = {
                "error": "Task results are missing from the task_handler module",
                "level": 2,
            }
            self.publish_result(error_dict, topic="postprocessing/data")
            logger.error("Task results are missing")
            return None
        logger.info(f"Task results: {self.task_results}")
        task_name = self.task_results.get("module_name")
        logger.info(f"Task name received from task_handler: {task_name}")
        self.publish_result(
            {
                "results": self.task_results,
                "prompt": self.prompt,
                "emotions": self.user_emotions,
                "user_data": self.user_data,
            },
            topic="postprocessing/data",
        )
        return None

    def _handle_postprocessing_module(self, input_data: dict):
        logger.info("Received preprocessing module data")
        self.response = input_data.get("response")
        self.robot_emotion = input_data.get("robot_emotion", "neutral")
        self.robot_emotion = self.robot_emotion.lower()
        is_error = input_data.get("is_error", False)
        if not self.response:
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.response = random.choice(ERROR_RESPONSES)
            self.robot_emotion = "error"
            self.publish_result(
                {
                    "is_error": True,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=True)
            logger.error("Response is missing in the preprocessing method")
            return None
        logger.info("Returning the preprocessing method result to the server")
        logger.info(f"Response: {self.response}")
        logger.info(f"Robot emotion: {self.robot_emotion}")
        logger.info(f"Is error: {is_error}")
        if is_error:
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.robot_emotion = "error"
            self.publish_result(
                {
                    "is_error": True,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=True)
        else:
            self.end_time = time.time()
            self.execution_time = self.end_time - self.start_time
            self.publish_result(
                {
                    "is_error": False,
                    "response": self.response,
                    "target_robot_id": self.robot_id,
                    "screen": self.robot_emotion,
                    "time_taken": self.execution_time,
                },
                topic="server/main",
            )
            self._publish_to_app(is_error=False)
        return None


# =========================
# Script Entry Point
# =========================
if __name__ == "__main__":
    main = Main()
    main.start_mqtt()
