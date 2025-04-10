import sys
from pathlib import Path

import os
from dotenv import load_dotenv
from tavily import TavilyClient
import logging

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utilities import BaseMQTTHandler

# Todo: Add Gemini usage to the pipeline to ensure that the answer is correct

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class GeneralQuestions(BaseMQTTHandler):
    """
    GeneralQuestions is a class for handling general knowledge or factual queries.
    """

    def __init__(self):
        """
        Initialize the GeneralQuestions object.
        """
        # Initialize BaseMQTTHandler with MQTT topics
        super().__init__(sub_topic="task_handler/general_questions", name="general_questions")
        
        self.tavily = TavilyClient(os.getenv("TAVILY_API_KEY_TEST")) #! Test

    def clean_answer(self, answer: str) -> str:
        """
        Cleans the answer string by removing unwanted characters.
        Args:
            answer (str): The answer string to clean.
        Returns:
            str: The cleaned answer string.
        """
        cleaned_answer = "".join(char for char in answer if ord(char) < 128)
        cleaned_answer = (
            cleaned_answer.strip()
        )  # Remove leading and trailing whitespace
        return cleaned_answer

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the general question processing.
        """
        query = input_data.get("query")
        topic = input_data.get("topic", "general")
        
        if not query:
            logger.error("Query is empty or not provided.")
            result = {"error": "Query is empty or not provided."}

        else:
            try:
                response = self.tavily.search(query, include_answer=True, topic=topic)
                logger.info(f"Response from Tavily API: {response}")
            except Exception as e:
                logger.error(f"Error in Tavily API: {e}")
                result = {"error": f"Error in Tavily API: {e}"}
            else:
                answer = self.clean_answer(response["answer"])
                result = {
                    "query": query,
                    "answer": answer,
                    "topic": topic,
                }
                
        self.publish_result(result, "task_handler/main")
        
        return None


if __name__ == "__main__":
    general_questions = GeneralQuestions()
    general_questions.start()
