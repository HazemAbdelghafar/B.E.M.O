from dotenv import dotenv_values, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSerializable
import os
from datetime import datetime

import sys
from pathlib import Path
import logging


# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utilities import BaseMQTTHandler, POST_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


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
        os.environ["GOOGLE_API_KEY"] = dotenv_values(find_dotenv())["GEMINI_API_KEY_TEST"] #! Test
        self.__llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.9,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.__system_prompts = self.__initialize_prompts()
        self.__chains = self.__initialize_chains()
        
                                        
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
        
        if not task_output:
            logger.error("Input results are missing")
            return {"error": "Input results are missing", "level": 2}
        if not isinstance(task_output, dict):
            logger.error("Input results are not a dictionary")
            return {"error": "Input results are not a dictionary", "level": 2}
        
        if not prompt:
            logger.error("Prompt is missing")
            return {"error": "Prompt is missing", "level": 2}
        
        module_name = task_output.get("module_name")
        
        if not module_name:
            logger.error("Module name is missing")
            return {"error": "Module name is missing", "level": 2}
        
        logger.info(f"Module name: {module_name}")        
        
        response = None
        result = {}
        
        try:
            response = self.__chains[module_name].invoke({"user_query": prompt, "task_output": task_output, "current_time": datetime.now(), "user_emotions": emotions})
        except Exception as e:
            logger.error(f"Error: {e}")
            response = None
            result = {"error": str(e), "level": 2, "method": module_name}

        if response is None:
            return result

        try: 
            result = response.content
        except Exception as e:
            logger.error(f"Error: {e}")
            result = {"error": str(e), "level": 2, "method": module_name}
        
        result = self.clean_output(result)
        
        # Publish the result
        return {
            "output": result
        }
        
    def clean_output(self, output: str) -> str:
        """
        Cleans the output string.
        
        Args:
            output (str): The output string to clean.
        
        Returns:
            str: The cleaned output string.
        """
        
        # Remove extra spaces
        output = " ".join(output.split())
        
        # Remove new lines
        output = output.replace("\n", "")
        
        # Remove extra spaces from the beginning and end
        output = output.strip()
        
        return output
                            
if __name__ == "__main__": 
    pp = PostProcessing()
    pp.start_mqtt()