import os
import json
import pyttsx3
from dotenv import load_dotenv
import google.generativeai as gai
from home_automation import control_device

load_dotenv()

class GAI:
    def __init__(self,model_name, SYSTEM_INSTRUCTION):
        self.SYSTEM_INSTRUCTION = SYSTEM_INSTRUCTION
        gai.configure(api_key=os.getenv('GEMINI_API'))
        self.model = gai.GenerativeModel(model_name, system_instruction=SYSTEM_INSTRUCTION)
        self.engine = pyttsx3.init()
        
    def generate_response(self, request: str):
        print("Generating response")
        response = self.model.generate_content(request)
        response = json.loads(response.text[8:-4])
        return response
    
    def action_handler(self,response: json):
        if response['method'] == 'smart home':
            control_device(response['switch'],response['status'])
            self.engine.say(response['reply'])
            self.engine.runAndWait()
            self.engine.stop()
            
    def take_action(self, request: str):
        response = self.generate_response(request)
        self.action_handler(response)
            
            
        
if __name__ == "__main__":
    SYSTEM_INSTRUCTION  = '''
    You are a robot named BEMO. Your job is to help the user anything they ask for. You will recieve text from the user and you should reply in a string format. Here is an example of a request and its reply: 

    request: Hey BEMO, can you add toothpaste to my shopping cart?

    # reply
    {
        "user's_emotion" : "neutral",
        "method" : "shop",
        "request" : "Add toothpaste to shopping cart",
        "reply": "Your item has been added to your shopping cart"
    }

    When the method detected is smart home as the following, the output should look like this:

    request: Hey BEMO, turn on switch one in my room

    # reply
    {
        "user's_emotion" : "neutral",
        "method" : "smart home",
        "switch" : "switch_1",
        "status" : "on",
        "reply": "switch 1 is turned on"
    }

    The switch should be written as previous. Example "switch_n". The status should be either on or off only.
    
    You shold state the user's emotion based on their words, the method the user is requesting, and the the request they have asked for. The methods that you can choose from are the following:  printing (3D printing request), general question (the user is asking a general question), shop (The user is requesting to add items to their shopping cart)'''
    MODEL_NAME = 'gemini-1.5-flash-8b'
    print(os.getenv('GEMINI_API'))

    llm = GAI(MODEL_NAME, SYSTEM_INSTRUCTION)
    test_request = input("Enter your prompt: ")
    llm.take_action(test_request)

