import sys
from pathlib import Path

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os
import json
import time
from dotenv import load_dotenv
from tavily import TavilyClient
from utils import BaseMQTTHandler

# Todo: Add Gemini usage to the pipeline to ensure that the answer is correct

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)


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
        self.tavily = TavilyClient(os.getenv("TAVILY_API"))

    def read_request(self, request_path: str = None):
        if request_path:
            with open(request_path, "r") as f:
                return json.load(f)
        else:
            with open(DEFAULT_PATH + "/request.json", "r") as f:
                return json.load(f)

    def write_response(self, data: dict):
        with open(DEFAULT_PATH + "/response.json", "w") as f:
            json.dump(data, f, indent=4)

    def clean_answer(self, answer: str):
        # Remove any extra characters and end of sentence characters
        cleaned_answer = "".join(char for char in answer if ord(char) < 128)
        cleaned_answer = (
            cleaned_answer.strip()
        )  # Remove leading and trailing whitespace
        return cleaned_answer

    def get_response(self, request_path: str = None):
        request = self.read_request(request_path)
        start_time = time.time()
        response = self.tavily.search(
            request["query"], include_answer=True, topic=request["topic"]
        )
        cleaned_answer = self.clean_answer(response["answer"])
        response_json = {
            "response": cleaned_answer,
            "time": round(time.time() - start_time, 2),
        }
        self.write_response(response_json)

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the general question processing.
        """
        query = input_data.get("query", "default_query")
        topic = input_data.get("topic", "general")
        start_time = time.time()
        response = self.tavily.search(query, include_answer=True, topic=topic)
        answer = self.clean_answer(response["answer"])
        result = {
            "query": query,
            "answer": answer,
            "topic": topic,
            "time": round(time.time() - start_time, 2),
        }
        return {
            "method": "general_questions",
            "result": result,
        }


if __name__ == "__main__":
    general_questions = GeneralQuestions()
    general_questions.start()
