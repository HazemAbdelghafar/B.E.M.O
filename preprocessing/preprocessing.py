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
from utilities import BaseMQTTHandler, PRE_SYSTEM_PROMPT, SwitchMapping, UserData

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

# Define the name of the module and the topics
NAME = "preprocessing"
SUB_TOPIC = "preprocessing/data"

LIMITS = {
    "smart_home": 3,
    "todo": 7,
    "mail": 7,
    "general": 10,
    "learning_resources": 3,
    "others": 3,
}

class PreProcessing(BaseMQTTHandler):
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
        self.__output_parser = JsonOutputParser()
        self.__system_prompts = self.__initialize_prompts()
        self.__chains = self.__initialize_chains()
        self.__chat_history = self.initialize_chat_history()
        self.__switch_mapping = SwitchMapping().get_all_mappings()
        self.__user_data = UserData().get_all_user_data()
        
    def initialize_chat_history(self) -> dict:
        """
        Initializes the chat history.
        
        Returns:
            dict: The initialized chat history.
        """
        
        # Initialize the chat history
        chat_history = {}
        
        # Add the system prompts to the chat history
        for key, value in PRE_SYSTEM_PROMPT.items():
            chat_history[key] = []
        
        return chat_history
                                        
    def __initialize_prompts(self) -> dict[str, PromptTemplate]:
        """
        Initializes the prompts.
        
        Returns:
            dict[str, PromptTemplate]: The initialized prompts.
        """
        
        # Initialize the prompts
        initialized_prompts = {}
        
        # Add the system prompts to the initialized prompts
        for key, value in PRE_SYSTEM_PROMPT.items():
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
    
    
    def limit_chat_history(self, label: str) -> None:
        """
        Limits the chat history for a given label.
        
        Args:
            label (str): The label to limit the chat history for.
        """
        
        # Limit the chat history
        if len(self.__chat_history[label]) > LIMITS[label]:
            self.__chat_history[label] = self.__chat_history[label][-LIMITS[label]:]
                    
    
    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        
        Args:
            input_data (dict): The input data to process.
        
        Returns:
            dict: The result of the classification.
        """
                
        # Get the prompt and labels from the input data
        prompt = input_data.get("prompt")
        labels = input_data.get("predicted_labels")
        
        if not prompt:
            logger.error("Prompt is missing")
            return {"error": "Prompt is missing", "level": 2}
        
        if not labels:
            logger.error("Labels are missing")
            return {"error": "Labels are missing", "level": 2}
                
        # Initialize the results
        results = []
        
        for label in labels:
            logger.info(f"Label: {label}")
            response = None
            try:
                response = self.__chains[label].invoke({"prompt": prompt, "current_time": datetime.now(), "chat_history": self.__chat_history[label], "switch_mapping": self.__switch_mapping, "user_data_name": self.__user_data['name'], "user_data_job_title": self.__user_data['job_title'], "user_data_location": self.__user_data['location'], "user_data_age": self.__user_data['age']})
            except Exception as e:
                logger.error(f"Error: {e}")
                response = None
                results.append({"error": str(e), "level": 2, "method": label})

            if response is None:
                self.publish_result(results[-1])
                continue

            error = ""
            try: 
                results.append(self.__output_parser.parse(response.content))
            except Exception as e:
                logger.error(f"Error: {e}")
                error += str(e) + " "
                cleaned_json = self.clean_json(response.content)
                try:
                    results.append(literal_eval(cleaned_json))
                except Exception as e:
                    logger.error(f"Error: {e}")
                    error += str(e) + " "
                    try:
                        results.append(json.loads(cleaned_json))
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        error += str(e) + " "
                        results.append({"error": error, "level": 2, "method": label})
            
            # Add the response to the chat history
            self.__chat_history[label].append({"human": prompt, "assistant": response.content})
            
            # Limit the chat history
            self.limit_chat_history(label)
            
            # Publish the result
            publish_result = results[-1]
            if isinstance(publish_result, list):
                publish_result = publish_result[0]
            
            self.publish_result(publish_result)

if __name__ == "__main__": 
    pp = PreProcessing()
    pp.start_mqtt()