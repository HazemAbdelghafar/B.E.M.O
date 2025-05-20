from dotenv import dotenv_values, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSerializable
from langchain_core.output_parsers import JsonOutputParser
import json
from ast import literal_eval
import os
from datetime import datetime

import sys
from pathlib import Path
import logging


# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utilities import BaseMQTTHandler, POST_SYSTEM_PROMPT, SwitchMapping, UserData

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

# Define the name of the module and the topics
NAME = "postprocessing"
SUB_TOPIC = "postprocessing/data"


class PostProcessing(BaseMQTTHandler):
    """
    TaskClassifier is a class for classifying tasks based on a given prompt.
    """

    def __init__(self):
        """
        Initialize the TaskClassifier object.
        """

        # Initialize the BaseMQTTHandler object
        super().__init__(SUB_TOPIC, NAME)

        # Initialize the ChatGoogleGenerativeAI object
        os.environ["GOOGLE_API_KEY"] = dotenv_values(find_dotenv())[
            "GEMINI_API_KEY_TEST"
        ]  #! Test
        self.__llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.9,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.__system_prompts = self.__initialize_prompts()
        self.__chains = self.__initialize_chains()
        self.__switch_mapping = SwitchMapping().get_all_mappings()
        self.__user_data = UserData().get_all_user_data()
        self.__output_parser = JsonOutputParser()

    def __initialize_prompts(self) -> dict[str, PromptTemplate]:
        """
        Initializes the prompts.

        Returns:
            dict[str, PromptTemplate]: The initialized prompts.
        """

        # Initialize the prompts
        initialized_prompts = {}

        # Add the system prompts to the initialized prompts
        for key, value in POST_SYSTEM_PROMPT.items():
            initialized_prompts[key] = PromptTemplate.from_template(value)

        return initialized_prompts

    def __initialize_chains(self) -> dict[str, RunnableSerializable]:
        """
        Initializes the chains.

        Returns:
            dict[str, RunnableSerializable]: The initialized chains.
        """

        # Initialize the chains
        initialized_chains = {}

        # Add the language model to the prompts
        for key, value in self.__system_prompts.items():
            initialized_chains[key] = value | self.__llm

        return initialized_chains

    def clean_json(self, json_str: str) -> str:
        """
        Cleans the JSON string.

        Args:
            json_str (str): The JSON string to clean.

        Returns:
            str: The cleaned JSON string.
        """

        # Clean the JSON string
        json_str = json_str.replace("```json", "").replace("```", "").strip()

        return json_str

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the classification.
        """

        # Get the prompt and labels from the input data
        task_output = input_data.get("results")
        prompt = input_data.get("prompt")
        emotions = input_data.get("emotions")
        error = input_data.get("error", None)

        if not task_output and not error:
            logger.error("Input results are missing")
            return {"error": "Input results are missing", "level": 4}

        if not isinstance(task_output, dict) and not error:
            logger.error("Input results are not a dictionary")
            return {"error": "Input results are not a dictionary", "level": 4}

        if not prompt and not error:
            logger.error("Prompt is missing")
            return {"error": "Prompt is missing", "level": 4}

        if not error:
            module_name = task_output.get("module_name")
        else:
            module_name = ""

        if not module_name and not error:
            logger.error("Module name is missing")
            return {"error": "Module name is missing", "level": 4}
        else:
            logger.info(f"Module name: {module_name}")

        response = None
        result = {}

        if error:
            module_name = "error"
            llm_input_dict = {"error_dict": input_data}
        else:
            llm_input_dict = {
                "user_query": prompt,
                "task_output": task_output,
                "current_time": datetime.now(),
                "user_emotions": emotions,
                "switch_mapping": self.__switch_mapping,
                "user_data_name": self.__user_data["name"],
                "user_data_job_title": self.__user_data["job_title"],
                "user_data_location": self.__user_data["location"],
                "user_data_age": self.__user_data["age"],
            }

        try:
            response = self.__chains[module_name].invoke(llm_input_dict)
        except Exception as e:
            logger.error(f"Error: {e}")
            result = {"error": str(e), "level": 4, "method": module_name}
            return result

        try:
            response_content = response.content
        except Exception as e:
            logger.error(f"Error: {e}")
            result = {"error": str(e), "level": 4, "method": module_name}
            return result

        error_str = ""
        try:
            result = self.__output_parser.parse(response_content)
        except Exception as e:
            logger.error(f"Error: {e}")
            error_str += str(e) + " "
            cleaned_json = self.clean_json(response_content)
            try:
                result = literal_eval(cleaned_json)
            except Exception as e:
                logger.error(f"Error: {e}")
                error_str += str(e) + " "
                try:
                    result = json.loads(cleaned_json)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    error_str += str(e) + " "
                    result = {"error": error_str, "level": 4, "method": module_name}

        is_error_str = True if result.get("error") else False
        is_error = True if error else False

        # Combine the error flags
        is_error_final = is_error_str or is_error

        result["is_error"] = is_error_final

        # Publish the result
        return result


if __name__ == "__main__":
    pp = PostProcessing()
    pp.start_mqtt()
