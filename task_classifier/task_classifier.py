import pickle
import os
import string
import logging

from dotenv import find_dotenv, dotenv_values
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain, RunnableConfig

import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utilities import BaseMQTTHandler, TASK_CLASSIFIER_PROMPT

# Specify the paths to the model and labels
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = f"{CURRENT_DIR}/models/TC_Pipeline_LR_v4.pkl"
LABELS_PATH = f"{CURRENT_DIR}/models/labels_v2.pkl"

# Define the name of the module and the topics
NAME = "task_classifier"
SUB_TOPIC = "task_classifier/prompt"

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class TaskClassifier(BaseMQTTHandler):
    """
    TaskClassifier is a class for classifying tasks based on a given prompt.
    """
    
    def __init__(self, use_llm: bool = True):

        """
        Initialize the TaskClassifier object.
        """
        
        # Initialize the BaseMQTTHandler object
        super().__init__(SUB_TOPIC, NAME)
        
        
        self.use_llm = use_llm

        if self.use_llm:
            # Initialize the LLM model here if needed
            os.environ["GOOGLE_API_KEY"] = dotenv_values(find_dotenv())["GEMINI_API_KEY_TEST"] #! Test
            self.__llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
            self.__output_parser = JsonOutputParser()
            self.__prompt = self._init_prompt()
            self.__chain = self._init_chain()
        else:
            # Load the model and labels
            self.__model = pickle.load(open(MODEL_PATH, "rb"))
            self.__labels = pickle.load(open(LABELS_PATH, "rb"))

    def _init_prompt(self) -> ChatPromptTemplate:
        """
        Initialize the prompt with the given text

        Args:
            None

        Returns:
            ChatPromptTemplate: The initialized prompt
        """

        return ChatPromptTemplate(
            [
                ("system", TASK_CLASSIFIER_PROMPT),
                ("human", "{user_input}"),
                ("placeholder", "{messages}"),
            ]
        )
        
    def _init_chain(self) -> chain:
        """
        Initializes the chain of runnables for the LLM to generate responses

        Args:
            None

        Returns:
            chain: The chain of run

        """
        return self.__prompt | self.__llm


        
    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        
        Args:
            input_data (dict): The input data to process.
        
        Returns:
            dict: The result of the classification.
        """
        prompt = input_data.get("prompt") # Get the prompt from the input data
        if not prompt:
            return {"error": "Prompt not provided", "level": 1}
        
        if self.use_llm:

            @chain
            def tool_chain(user_input: str, config: RunnableConfig):
                input_ = {"user_input": user_input}
                try:
                    ai_msg = self.__chain.invoke(input_, config=config)
                except Exception as e:
                    raise ValueError("Error in LLM tool chain") from e

                try:
                    parsed_output = self.__output_parser.parse(ai_msg.content)
                except Exception as e:
                    raise ValueError("Error parsing LLM output") from e

                return parsed_output
            
            try:
                result = tool_chain.invoke(prompt)
            except Exception as e:
                return {"error": str(e), "level": 2}
            
            labels = result.get("predicted_labels")
            if not labels:
                return {"error": "No labels found in the response", "level": 2}
            prompts = result.get("split_prompts")
            if not prompts:
                return {"error": "No prompts found in the response", "level": 2}
            if len(labels) != len(prompts):
                return {"error": "Mismatch between labels and prompts", "level": 2}
            
            # Create a dictionary to store the results
            result_dict = {"predicted_labels": labels, "split_prompts": prompts}
            
            return result_dict

        else:
            try:
                prompt = self.preprocess_prompt(prompt) # Preprocess the prompt
                prediction = self.__model.predict([prompt])[0] # Make a prediction using the model
                
                # Get the predicted labels based on the prediction
                predicted_labels = [self.__labels[i] for i, val in enumerate(prediction) if val == 1]
            except Exception as e:
                return {"error": str(e), "level": 2}
                
            # Return the predicted labels
            return {"predicted_labels": predicted_labels}
        
    def preprocess_prompt(self, prompt: str) -> str:
        """
        Preprocess the prompt for classification.
        
        Args:
            prompt (str): The prompt to preprocess.
        
        Returns:
            str: The preprocessed prompt.
        """
        
        # Remove punctuation
        prompt = prompt.translate(str.maketrans('', '', string.punctuation))
        
        # Lowercase
        prompt = prompt.lower()
                        
        # Remove extra spaces
        prompt = " ".join(prompt.split())
        
        return prompt
            
if __name__ == "__main__":
    tc = TaskClassifier()
    tc.start_mqtt()



