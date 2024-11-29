import os
import json
import time
from dotenv import load_dotenv
from tavily import TavilyClient

# Todo: Add Gemini usage to the pipeline to ensure that the answer is correct

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)

class GeneralQuestions:
    def __init__(self):
        self.tavily = TavilyClient(os.getenv("TAVILY_API"))
        
    def read_request(self, request_path:str = None):
        if request_path:
            with open(request_path, "r") as f:
                return json.load(f)
        else:
            with open(DEFAULT_PATH + '/request.json', "r") as f:
                return json.load(f)
        
    def write_response(self, data:dict):
        with open(DEFAULT_PATH + '/response.json', 'w') as f:
            json.dump(data, f, indent=4)
        
    def clean_answer(self,answer:str):
        # Remove any extra characters and end of sentence characters
        cleaned_answer = "".join(char for char in answer if ord(char) < 128)
        cleaned_answer = cleaned_answer.strip()  # Remove leading and trailing whitespace
        return cleaned_answer
    
    def get_response(self, request_path:str = None):
        request = self.read_request(request_path)
        start_time = time.time()
        response = self.tavily.search(request['query'], include_answer=True, topic=request['topic'])
        cleaned_answer = self.clean_answer(response['answer'])
        response_json = {'response': cleaned_answer, 'time': time.time() - start_time}
        self.write_response(response_json)
        

if __name__== "__main__":
    general_questions = GeneralQuestions()
    general_questions.get_response()