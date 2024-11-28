import os
import json
import numpy as np
import pyaudio
from transformers import pipeline
from queue import Queue
from threading import Thread
from time import time
import wave

def transcribe_wav_file(model_name, file_path):
    """
    Transcribe audio from a WAV file.
    """
    import whisper

    model = whisper.load_model(model_name)
    with wave.open(file_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        num_frames = wf.getnframes()
        audio_data = wf.readframes(num_frames)
    
    start_time = time()
    transcription = model.transcribe(audio_data, sample_rate=sample_rate)
    end_time = time()
    print(f"\nTranscription: {transcription['text']}")
    print(f"Classification: {transcription['language']}")
    print(f"Start Time: {start_time}, End Time: {end_time}")


# Classification function
def classify_event(text):
    """
    Classify events based on the transcription text.
    """
    text = text.lower()
    if any(keyword in text for keyword in ["bemo", "bmo", "vemo", "vmo", "nemo", "kemo", "bbmo", "moo", "bemoo", "bemu", "temo"]):
        return "bemo"
    elif "screaming" in text:
        return "screaming"
    elif "music" in text:
        if "dramatic" in text:
            return "dramatic_music"
        return "music"
    elif "blank audio" in text:
        return "blank_audio"
    elif "crowd talking" in text:
        return "crowd_talking"
    elif "laughing" in text:
        return "laughing"
    return "other"


# Save transcription to JSON
def save_to_json(transcription, classification, start_time, end_time, json_file="transcriptions_W_o.json"):
    """
    Save transcription and classification to a JSON file.
    """
    event = {
        "text": transcription,
        "classification": classification,
        "start_time": start_time,
        "end_time": end_time
    }

    # Check and clear JSON file if it exceeds 50MB
    clear_json_file_if_exceeds_size(json_file, max_size_mb=50)

    # Write event to JSON file
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


def clear_json_file_if_exceeds_size(json_file, max_size_mb=50):
    """
    Clear the JSON file if it exceeds the specified size.
    """
    if os.path.exists(json_file):
        file_size_mb = os.path.getsize(json_file) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            print(f"JSON file size exceeds {max_size_mb}MB. Clearing file...")
            with open(json_file, "w") as file:
                json.dump([], file, indent=4)


# Real-time transcription and classification
def real_time_transcription(model_name="openai/whisper-base", sample_rate=16000, chunk_size=1024):
    """
    Perform real-time transcription and classification using Hugging Face's Whisper model.
    """
    print(f"Loading Whisper model: {model_name}")
    transcriber = pipeline(model=model_name, task="automatic-speech-recognition")

    # Initialize PyAudio
    audio_stream = pyaudio.PyAudio()
    queue = Queue()

    # Audio input stream callback
    def callback(in_data, frame_count, time_info, status):
        queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    # Open audio stream
    stream = audio_stream.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size,
        stream_callback=callback
    )
    stream.start_stream()

    print("Model loaded. Listening for audio...\n")

    audio_buffer = b""
    recording_start_time = None  # Start time of the current recording

    try:
        while True:
            # Collect audio data from the queue
            while not queue.empty():
                audio_buffer += queue.get()

            # Process audio buffer if it exceeds a threshold
            if len(audio_buffer) > sample_rate * 2:  # ~2 seconds of audio
                audio_np = np.frombuffer(audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
                audio_buffer = b""  # Clear the buffer

                # Set the recording start time if it's the first chunk
                if recording_start_time is None:
                    recording_start_time = time()

                # Calculate start and end times
                current_time = time()
                start_time = recording_start_time
                end_time = current_time
                recording_start_time = current_time

                # Transcribe the audio data
                result = transcriber(audio_np)
                transcription = result.get("text", "").strip()

                # Classify the transcription
                classification = classify_event(transcription)

                # Save transcription to JSON
                save_to_json(transcription, classification, start_time, end_time)

                # Print transcription and classification
                print(f"\nTranscription: {transcription}")
                print(f"Classification: {classification}")
                print(f"Start Time: {start_time}, End Time: {end_time}")
    except KeyboardInterrupt:
        print("\nStopping transcription...")
    finally:
        stream.stop_stream()
        stream.close()
        audio_stream.terminate()


# Main function
def main():
    """
    Main function to handle real-time transcription.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Real-time transcription and classification using Whisper.")
    parser.add_argument("--model", default="openai/whisper-base", help="Whisper model to use (default: openai/whisper-base).")
    parser.add_argument("--sample_rate", default=16000, type=int, help="Audio sample rate (default: 16000 Hz).")
    parser.add_argument("--chunk_size", default=1024, type=int, help="Audio chunk size (default: 1024 frames).")
    args = parser.parse_args()

    real_time_transcription(model_name=args.model, sample_rate=args.sample_rate, chunk_size=args.chunk_size)



########################wav file################################
# def main():
#     """
#     Main function to handle real-time transcription or transcription from a WAV file.
#     """
#     import argparse

#     parser = argparse.ArgumentParser(description="Real-time transcription and classification using Whisper.")
#     parser.add_argument("--model", default="openai/whisper-base", help="Whisper model to use (default: openai/whisper-base).")
#     parser.add_argument("--sample_rate", default=16000, type=int, help="Audio sample rate (default: 16000 Hz).")
#     parser.add_argument("--chunk_size", default=1024, type=int, help="Audio chunk size (default: 1024 frames).")
#     parser.add_argument("--file", help="Path to the WAV file for transcription.")
#     args = parser.parse_args()

#     if args.file:
#         transcribe_wav_file(model_name=args.model, file_path=args.file)
#     else:
#         real_time_transcription(model_name=args.model, sample_rate=args.sample_rate, chunk_size=args.chunk_size)


if __name__ == "__main__":
    main()
