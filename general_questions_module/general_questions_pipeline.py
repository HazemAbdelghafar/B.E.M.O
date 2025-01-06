import os
import json
import time
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)


class GeneralQuestions:
    def __init__(self, save_read_json: bool = False):
        self.tavily = TavilyClient(os.getenv("TAVILY_API_KEY_TEST")) #! Change to os.getenv("TAVILY_API_KEY") for production
        self.save_read_json = save_read_json
        
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

    def get_response(self, request_path: str = None, request: dict = None):
        if self.save_read_json:
            request = self.read_request(request_path)
            
        response = self.tavily.search(
            request["query"], include_answer=True, topic=request["topic"]
        )
        cleaned_answer = self.clean_answer(response["answer"])
        response_dict = {
            "response": cleaned_answer,
        }
        if self.save_read_json:
            self.write_response(response_dict)
            return response_dict
        else:
            return cleaned_answer


if __name__ == "__main__":
    general_questions = GeneralQuestions()
    input_dict = {
        "query": "Tell me about AAST's Alamein branch",
        "topic": "general"
    }
    response = general_questions.get_response(request=input_dict)
    print(response)