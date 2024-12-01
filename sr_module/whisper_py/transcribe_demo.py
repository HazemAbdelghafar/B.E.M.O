
import argparse
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
import argparse


# def transcribe_wav(file_path, model="base"):
#     """
#     Transcribe a WAV file using Whisper.

#     Parameters:
#         file_path (str): Path to the WAV file.
#         model (str): Whisper model to use ("base", "small", "medium", "large").

#     Returns:
#         List[dict]: A list of transcription segments with start/end times and text.
#     """
#     # Load the Whisper model
#     print(f"Loading Whisper model: {model}")
#     audio_model = whisper.load_model(model)

#     # Open the WAV file
#     try:
#         with wave.open(file_path, "rb") as wav_file:
#             num_channels = wav_file.getnchannels()
#             frame_rate = wav_file.getframerate()
#             num_frames = wav_file.getnframes()

#             print(f"Processing WAV file: {file_path}")
#             print(f"Channels: {num_channels}, Frame Rate: {frame_rate}, Frames: {num_frames}")

#             # Read audio data and convert to numpy array
#             audio_data = wav_file.readframes(num_frames)
#             audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
#     except Exception as e:
#         print(f"Error reading WAV file: {e}")
#         return []

#     # Transcribe audio
#     print("Transcribing audio...")
#     result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())

#     # Extract transcription and return results
#     segments = []
#     for segment in result.get("segments", []):
#         segments.append({
#             "start_time": segment["start"],
#             "end_time": segment["end"],
#             "text": segment["text"]
#         })

        

#     return segments

def classify_event(line):
    line = line.lower()
    if any(keyword in line for keyword in ["bemo", "bmo", "vemo", "vmo", "nemo", "kemo", "bbmo", "moo", "bemoo", "bemu", "temo"]):
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




def save_to_json(transcription, cleaned_text, classification, start_time, end_time, json_file="transcriptions_demo.json"):
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
# Main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="base", help="Model to use",
                        choices=["base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the English model.")
    parser.add_argument("--energy_threshold", default=300,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real-time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before considering it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    phrase_time = None
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = True

    if 'linux' in platform:
        mic_name = args.default_microphone
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

    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = []

    with source:
        recorder.adjust_for_ambient_noise(source)
        print("Adjusting for ambient noise. Please wait...")

    def record_callback(_, audio: sr.AudioData) -> None:
        print("Audio captured.")
        data = audio.get_raw_data()
        data_queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    print(f"Model '{model}' loaded. Listening...\n")

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False

                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True

                phrase_time = now

                # Process audio data
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result.get('text', '').strip()

                if result.get('segments'):
                    start_time = result['segments'][0]['start']
                    end_time = result['segments'][-1]['end']
                else:
                    start_time, end_time = 0.0, 0.0

                classification = classify_event(text)

                # Save transcription to JSON
                save_to_json(text, text, classification, start_time, end_time)

                if phrase_complete:
                    transcription.append(text)
                else:
                    if transcription:
                        transcription[-1] = text
                    else:
                        transcription.append(text)

                os.system('cls' if os.name == 'nt' else 'clear')
                for line in transcription:
                    print(line)

                print('', end='', flush=True)
            else:
                sleep(0.25)
        except KeyboardInterrupt:
            print("\nStopping transcription...")
            break

    print("\n\nFinal Transcription:")
    for line in transcription:
        print(line)


# def main():
#     # Argument parser for command-line input
#     parser = argparse.ArgumentParser(description="Transcribe a WAV file with classification.")
#     parser.add_argument("wav_file", help="Path to the WAV file to transcribe.")
#     parser.add_argument("--model", default="base", help="Whisper model to use (base, small, medium, large).")
#     args = parser.parse_args()

#     # Transcribe the WAV file and classify segments
#     try:
#         print(f"Transcribing file: {args.wav_file} using model: {args.model}")
#         transcriptions = transcribe_wav(args.wav_file, model=args.model)

#         # Display the results with classification
#         print("\nTranscription Results with Classification:")
#         for segment in transcriptions:
#             print(f"[{segment['start_time']} - {segment['end_time']}] "
#                   f"({segment['classification']}): {segment['text']}")

#     except Exception as e:
#         print(f"An error occurred during transcription: {e}")




if __name__ == "__main__":
    main()
