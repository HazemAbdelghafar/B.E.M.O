import os
import re
import json
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)

class GeneralQuestions:
    def __init__(self):
        self.tavily = TavilyClient(os.getenv("TAVILY_API"))
        
    def read_request(self):
        with open(DEFAULT_PATH + '/request.json', "r") as f:
            return json.load(f)
        
    def write_response(self, data):
        with open(DEFAULT_PATH + '/response.json', 'w') as f:
            json.dump(data, f, indent=4)
        
    def clean_answer(self,answer):
        # Remove any extra characters and end of sentence characters
        cleaned_answer = re.sub(r'[^\w\s]', '', answer)  # Remove punctuation
        cleaned_answer = cleaned_answer.strip()  # Remove leading and trailing whitespace
        return cleaned_answer
    
    def get_response(self, path):
        request = self.read_request()
        response = self.tavily.search(request['query'], include_answer=True, topic=request['topic'])
        cleaned_answer = self.clean_answer(response['answer'])
        response_json = {'response': cleaned_answer}
        self.write_response(response_json)

if __name__== "__main__":
    general_questions = GeneralQuestions()
    general_questions.get_response(DEFAULT_PATH)