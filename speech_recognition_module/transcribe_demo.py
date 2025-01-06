import argparse
import wave
import os
import json
import numpy as np
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

# [
#             "hey bemo", "hey bmo", "hey vemo", "hey vmo", "hey nemo", "hey kemo",
#             "hey bbmo", "hey moo", "hey bemoo", "hey bemu",
#             "hey temo", "bey bemo", "bey bmo", "bey vemo",
#             "bey vmo", "bey nemo", "bey kemo", "bey bbmo",
#             "bey moo", "bey bemoo", "bey bemu", "bey temo",
#             "sey bemo", "sey bmo", "sey vemo", "sey vmo", "sey nemo",
#             "sey kemo", "sey bbmo", "sey moo", "sey bemoo", "sey bemu",
#             "sey temo", "ey bemo", "ey bmo", "ey vemo", "ey vmo", "ey nemo",
#             "ey kemo", "ey bbmo", "ey moo", "ey bemoo", "ey bemu", "ey temo"]


class SpeechRecognition:
    def __init__(self, model="large", non_english=False, energy_threshold=300, record_timeout=4.0, phrase_timeout=5.0, default_microphone=None):
        self.model = model
        self.non_english = non_english
        self.energy_threshold = energy_threshold
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.default_microphone = default_microphone
        self.phrase_time = None
        self.data_queue = Queue()
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = True
        self.transcription = []

    def classify_event(self, line):
        line = line.lower()
        
        detection_list = ['hey', 'bey', 'sey', 'ey', 'hi']
        
        if any(keyword in line for keyword in detection_list): 
            return "bemo"
        elif "screaming" in line:
            return "screaming"
        elif "music" in line:
            if "dramatic" in line:
                return "dramatic_music"
            return "music"
        elif "blank audio" in line:
            return "blank_audio"
        elif "crowd talking" in line:
            return "crowd_talking"
        elif "laughing" in line:
            return "laughing"
        return "other"

    def save_to_json(self, transcription, cleaned_text, classification, start_time, end_time, json_file="transcriptions_demo.json"):
        event = {
            "raw_text": transcription,
            "cleaned_text": cleaned_text,
            "classification": classification,
            "start_time": start_time,
            "end_time": end_time
        }

        if os.path.exists(json_file):
            with open(json_file, "r+") as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    data = []
                data.append(event)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(json_file, "w") as file:
                json.dump([event], file, indent=4)

    def record_callback(self, _, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)
    
    
    
    def run(self):
        if 'linux' in platform:
            mic_name = self.default_microphone
            if not mic_name or mic_name == 'list':
                return
            else:
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    if mic_name in name:
                        source = sr.Microphone(sample_rate=16000, device_index=index)
                        break
        else:
            source = sr.Microphone(sample_rate=16000)

        audio_model = whisper.load_model(self.model)

        with source:
            self.recorder.adjust_for_ambient_noise(source)

        stopper = self.recorder.listen_in_background(source, self.record_callback, phrase_time_limit=self.record_timeout)

        while True:
            try:
                now = datetime.utcnow()
                if not self.data_queue.empty():
                    phrase_complete = False

                    if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                        phrase_complete = True

                    self.phrase_time = now

                    # Process audio data
                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()

                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                    text = result.get('text', '').strip()

                    if result.get('segments'):
                        start_time = result['segments'][0]['start']
                        end_time = result['segments'][-1]['end']
                    else:
                        start_time, end_time = 0.0, 0.0

                    classification = self.classify_event(text)
                    if classification == "bemo":
                        print("Bemo detected!")
                        stopper()
                        return text


                    if phrase_complete:
                        self.transcription.append(text)
                    else:
                        if self.transcription:
                            self.transcription[-1] = text
                        else:
                            self.transcription.append(text)

                    os.system('cls' if os.name == 'nt' else 'clear')

                else:
                    sleep(0.25)
            except KeyboardInterrupt:
                break
            


if __name__ == "__main__":
    SpeechRecognition.main()
