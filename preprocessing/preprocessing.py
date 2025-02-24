from pprint import pprint
from dotenv import dotenv_values, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSerializable
from langchain_core.output_parsers import JsonOutputParser
import json
from ast import literal_eval
import os

import sys
from pathlib import Path


# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import BaseMQTTHandler, SYSTEM_PROMPTS, switch_mapping

# Define the name of the module and the topics
NAME = "preprocessing"
SUB_TOPIC = "preprocessing/prompt"

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
                                        
    def __initialize_prompts(self) -> dict[str, PromptTemplate]:
        """
        Initializes the prompts.
        
        Returns:
            dict[str, PromptTemplate]: The initialized prompts.
        """
        
        # Initialize the prompts
        initialized_prompts = {}
        
        # Add the system prompts to the initialized prompts
        for key, value in SYSTEM_PROMPTS.items():
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
        prompt = input_data["preprocessed_prompt"]
        labels = input_data["predicted_labels"]
                
        # Initialize the results
        results = []
        
        for label in labels:
            print(f"Label: {label}")
            response = None
            try:
                response = self.__chains[label].invoke({"prompt": prompt})
            except Exception as e:
                print(f"Error: {e}")
                response = None
                results.append({"method": label, "response": "", "error": str(e)})

            if response is None:
                self.publish_result_server(results[-1])
                continue

            error = ""
            try: 
                results.append(self.__output_parser.parse(response.content))
            except Exception as e:
                print(f"Error: {e}")
                error += str(e) + " "
                cleaned_json = self.clean_json(response.content)
                try:
                    results.append(literal_eval(cleaned_json))
                except Exception as e:
                    print(f"Error: {e}")
                    error += str(e) + " "
                    try:
                        results.append(json.loads(cleaned_json))
                    except Exception as e:
                        print(f"Error: {e}")
                        error += str(e) + " "
                        results.append({"method": label, "response": response.content, "error": error})
                        
            self.publish_result_server(results[-1])
                            
if __name__ == "__main__": 
    pp = PreProcessing()
        
    # Start the MQTT client loop
    pp.start()