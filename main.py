from communication_module.gmail_api import GmailAPI
from communication_module.tasks_api import TasksApi
from preprocessing.preprocessing import Preprocessing
from postprocessing.postprocessing import Postprocessing
from smart_home_module.home_automation import SmartHomeAutomation
from speech_recognition_module.transcribe_demo import SpeechRecognition
from general_questions_module.general_questions_pipeline import GeneralQuestions
from tts_module.text_to_speech import play_speech
import argparse
from sys import platform
import pyttsx3

class BEMO:
    def __init__(self):
        parser = argparse.ArgumentParser()
        self.gmail = GmailAPI('0')
        self.tasks = TasksApi('1')
        self.pre = Preprocessing()
        self.post = Postprocessing()
        self.home = SmartHomeAutomation()
        self.general = GeneralQuestions()
        self.is_rapid = False
        self.is_todo = False
        self.final_is = False
        
        parser.add_argument("--model", default="base.en", help="Model to use",
                            choices=["base.en", "small.en", "medium.en", "large"])
        parser.add_argument("--non_english", action='store_true',
                            help="Don't use the English model.")
        parser.add_argument("--energy_threshold", default=300,
                            help="Energy level for mic to detect.", type=int)
        parser.add_argument("--record_timeout", default=4.0,
                            help="How real-time the recording is in seconds.", type=float)
        parser.add_argument("--phrase_timeout", default=5.0,
                            help="How much empty space between recordings before considering it a new line in the transcription.", type=float)
        if 'linux' in platform:
            parser.add_argument("--default_microphone", default='pulse',
                                help="Default microphone name for SpeechRecognition. "
                                     "Run this with 'list' to view available Microphones.", type=str)
        args = parser.parse_args()

        self.sr = SpeechRecognition(
            model=args.model,
            non_english=args.non_english,
            energy_threshold=args.energy_threshold,
            record_timeout=args.record_timeout,
            phrase_timeout=args.phrase_timeout,
            default_microphone=args.default_microphone if 'linux' in platform else None
        )
        self.engine = pyttsx3.init()

        
    def action_handler(self, pre_response: dict):
        
        if self.is_todo and self.is_rapid and not self.final_is:
            self.final_is = True
            return self.gmail.create_send_draft(
                subject="Survey about the graduation project discussion",
                # recipients=["obadawy2@gmail.com", "yhanafy@aast.edu", "Osamahesham357@gmail.com", "hanysaid2000@aast.edu", "omar.o.shalash@aast.edu", "abouelfarag@aast.edu", "Aly.fahmy@gmail.com"]
                recipients=["begadtamim.a@gmail.com"],
                content = "Dear Doctors,\n\nWe are the six students working on BEMO: Begad Tamim, Mohamed Abdelnasser, Hazem Mohamed, Abdelrahman Saeed, Youssef Ayman, and Mohamed Abdulrahim. We'd greatly appreciate it if you could take a few minutes to complete this short survey: https://forms.gle/5Y1JhtdgEbq1gQ1TA\n\nThank you for your support!\n\nBest regards,\B.E.M.O's Team"
            )


        if self.is_rapid and not self.final_is:
            self.is_todo = True
            return self.tasks(
                {
                "method": "todo",
                "list_or_task": "task",
                "list_name": "my tasks",
                "task_name": "Send survey to the Doctors",
                "action": "insert",
                }
            )
        
        try:
            method = pre_response['method']
        except:
            return ''
        if method == 'rapid questions':
            self.is_rapid = True
            query = pre_response['query']
            if "arab" in query.lower():
                pre_response['query'] = "Tell me about the Arab Academy for Science, Technology, and Maritime Transport."
            return str(self.general.get_response(request=pre_response))
        elif method == 'smart home':
            return str(self.home.execute_switch_control(pre_response))
        elif method == 'todo':
            return str(self.tasks(pre_response))
        elif method == 'mail':
            return self.gmail.send_mail(pre_response)
            
    
    def pipeline(self):
        text = self.sr.run()
        print(text)
        pre_response = self.pre.generate_response(text)
        print(pre_response)
        status = self.action_handler(pre_response)
        print(status)
        try:
            method = pre_response['method']
        except:
            method = ''
        post_response = self.post(status, text, method)
        print(post_response)
        play_speech(post_response)
        with open('./output.txt', 'a+') as f:
            f.write(f"{text}\n{pre_response}\n {status}\n {post_response}\n\n\n" )
        
    
    
if __name__ == '__main__':
    bemo = BEMO()
    while True:
        bemo.pipeline()
        
    