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


class SpeechRecognitionDemo:
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
        print("Audio captured.")
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def run(self):
        if 'linux' in platform:
            mic_name = self.default_microphone
            if not mic_name or mic_name == 'list':
                print("Available microphone devices are: ")
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    print(f"Microphone with name \"{name}\" found")
                return
            else:
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    if mic_name in name:
                        source = sr.Microphone(sample_rate=16000, device_index=index)
                        break
        else:
            source = sr.Microphone(sample_rate=16000)

        if self.model != "large" and not self.non_english:
            self.model = self.model + ".en"
        audio_model = whisper.load_model(self.model)

        with source:
            self.recorder.adjust_for_ambient_noise(source)
            print("Adjusting for ambient noise. Please wait...")

        self.recorder.listen_in_background(source, self.record_callback, phrase_time_limit=self.record_timeout)
        print(f"Model '{self.model}' loaded. Listening...\n")

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
                        
                        return text

                    # Save transcription to JSON
                    # self.save_to_json(text, text, classification, start_time, end_time)

                    if phrase_complete:
                        self.transcription.append(text)
                    else:
                        if self.transcription:
                            self.transcription[-1] = text
                        else:
                            self.transcription.append(text)

                    os.system('cls' if os.name == 'nt' else 'clear')
                    for line in self.transcription:
                        print(line)

                    print('', end='', flush=True)
                else:
                    sleep(0.25)
            except KeyboardInterrupt:
                print("\nStopping transcription...")
                break

        print("\n\nFinal Transcription:")
        for line in self.transcription:
            print(line)

    @staticmethod
    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--model", default="base", help="Model to use",
                            choices=["base", "small", "medium", "large"])
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

        demo = SpeechRecognitionDemo(
            model=args.model,
            non_english=args.non_english,
            energy_threshold=args.energy_threshold,
            record_timeout=args.record_timeout,
            phrase_timeout=args.phrase_timeout,
            default_microphone=args.default_microphone if 'linux' in platform else None
        )
        return demo.run()

if __name__ == "__main__":
    SpeechRecognitionDemo.main()
