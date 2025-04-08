import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSerializable
from dotenv import dotenv_values, find_dotenv
import os
import random
import time
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(filename)s %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename='./logging.log',
    encoding='utf-8',
    level=logging.DEBUG
)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utilities import BaseMQTTHandler, POST_SYSTEM_PROMPT, ERROR_RESPONSES

class PostProcessing(BaseMQTTHandler):
    """
    A class to postprocess the result of a task into a natural, engaging response.
    """
    def __init__(self, sub_topic: str = "default_topic", name: str = "PostProcessing") -> None:
        """
        Initialize the Postprocessing class.
        
        Args:
            sub_topic (str): The subscription topic for the MQTT client.
            name (str): The name of the handler.
        
        Returns:
            None
        """
        super().__init__(sub_topic=sub_topic, name=name)  # Pass required arguments to the parent class
        self.name = name  # Explicitly set the name attribute
        random.seed(time.time())
        os.environ["GOOGLE_API_KEY"] = dotenv_values(find_dotenv())["GEMINI_API_KEY_TEST"] #! Test
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.9,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.prompts = self._init_prompt()
        self.chain = self._init_chain()
        self.tasks = [key for key in POST_SYSTEM_PROMPT.keys()]
        logger.info("PostProcessing initialized successfully.")

    def _init_prompt(self) -> dict:
        """
        Initialize the prompt for the task.
        
        Args:
            None
            
        Returns:
            dict: A dictionary of task-specific prompts.
        """
        initialized_prompts = {}
        for task, prompt in POST_SYSTEM_PROMPT.items():
            initialized_prompts[task] = PromptTemplate.from_template(prompt)
        logger.info("Prompts initialized successfully.")
        return initialized_prompts
            
    def _init_chain(self) -> RunnableSerializable:
        """
        Initialize the chain for the task.
        
        Args:
            None
        
        Returns:
            RunnableSerializable: The chain for the task.
        """
        logger.info("Chain initialized successfully.")
        return self.prompts | self.llm

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the PostProcessing class.
        
        Args:
            input_data (dict): The input data to process, containing task_result, user_query, and task_name.
        
        Returns:
            dict: The result of the postprocessing.
        """
        task_result = input_data.get("task_result", "")
        user_query = input_data.get("user_query", "")
        task_name = input_data.get("task_name", "")

        logger.info(f"Executing main with task_name: {task_name}, user_query: {user_query}, task_result: {task_result}")
        
        # Initialize the result
        result = {"task_name": task_name, "response": "", "error": ""}

        # Validate inputs
        if task_name not in self.tasks:
            error_message = f"Task name '{task_name}' not found in predefined tasks."
            logger.error(error_message)
            result["error"] = error_message
            return result
        
        if not user_query or not task_result or not task_name:
            error_message = "One or more inputs are empty."
            logger.error(error_message)
            result["error"] = error_message
            return result

        # Process the input
        try:
            response = self.chain.invoke(
                input={
                    "task_result": task_result,
                    "user_query": user_query,
                    "task_name": task_name
                }
            )
            try:
                result["response"] = response.content.strip()
                logger.info(f"Generated response: {result['response']}")
            except Exception as e:
                error_message = f"Error processing response content: {e}"
                logger.error(error_message)
                result["error"] = error_message
        except Exception as e:
            error_message = f"Error invoking chain: {e}"
            logger.error(error_message)
            result["error"] = error_message

        return result

if __name__ == "__main__":
    logger.info("Starting PostProcessing...")
    pp = PostProcessing()
    pp.start()