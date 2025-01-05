from communication_module.gmail_api import GmailAPI
from communication_module.tasks_api import TasksApi
from preprocessing.preprocessing import Preprocessing
from postprocessing.postprocessing import Postprocessing
from smart_home_module.home_automation import SmartHomeAutomation
from speech_recognition_module.transcribe_demo import SpeechRecognitionDemo
from general_questions_module.general_questions_pipeline import GeneralQuestions

class BEMO:
    def __init__(self):
        self.gmail = GmailAPI('0')
        self.tasks = TasksApi('0')
        self.pre = Preprocessing()
        self.post = Postprocessing()
        self.home = SmartHomeAutomation()
        self.general = GeneralQuestions()
        self.sr = SpeechRecognitionDemo()
        
    def action_handler(self, pre_response: dict):
        method = pre_response['method']
        if method == 'rapid questions':
            return self.general.get_response(pre_response)
        elif method == 'smart home':
            return self.home.execute_switch_control(pre_response)
        elif method == 'todo':
            return self.tasks(pre_response)
        elif method == 'mail':
            return self.gmail.send_mail(pre_response)

            
        pass
    
    
    def pipeline(self):
        text = self.sr.main()
        print(text)
        pre_response = self.pre.generate_response(text)
        print(pre_response)
        status = self.action_handler(pre_response)
        print(status)
        post_response = self.post(status)
        print(post_response)
        pass
    
    
if __name__ == '__main__':
    bemo = BEMO()
    bemo.pipeline()
    pass
    