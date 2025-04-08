from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSerializable
from dotenv import dotenv_values, find_dotenv
import os
import random
import time
import sys
from pathlib import Path

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
        self.client = self._init_client()  # Initialize the MQTT client
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
        
    def _init_client(self):
        """
        Initialize the MQTT client.

        Returns:
            MQTT client instance.
        """
        # Replace with actual MQTT client initialization logic
        return super()._init_client()

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
        return initialized_prompts
            
    def _init_chain(self) -> RunnableSerializable:
        """
        Initialize the chain for the task.
        
        Args:
            None
        
        Returns:
            RunnableSerializable: The chain for the task.
        """
        return self.prompts | self.llm
    
    def __call__(self, task_result: str, user_query: str, task_name: str) -> str:
            """
            Process the user query and task result to generate a response.

            Args:
                task_result (str): The result of the task.
                user_query (str): The user's query.
                task_name (str): The name of the task.

            Returns:
                str: The generated response.
            """
            
            if task_name not in self.tasks:
                return ERROR_RESPONSES[random.randint(0, len(ERROR_RESPONSES)-1)]
            
            if user_query == "" or task_result == "" or task_name == "":
                return ERROR_RESPONSES[random.randint(0, len(ERROR_RESPONSES)-1)]
            
            try:
                response = self.chain.invoke(
                    input={
                        "task_result": task_result,
                        "user_query": user_query,
                        "task_name": task_name
                    }
                )
                try:
                    response = response.content.strip()
                except:
                    response = ERROR_RESPONSES[random.randint(0, len(ERROR_RESPONSES)-1)]
            except:
                response = ERROR_RESPONSES[random.randint(0, len(ERROR_RESPONSES)-1)]
                
            return response
        
        
    
    
if __name__ == "__main__":
    pp = PostProcessing()
    pp.start()