import os
import sys
import io
import hashlib
import pygame
import random
import time
import tempfile
import requests
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import your base MQTT handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utilities import BaseMQTTHandler, ERROR_RESPONSES

# Setup cache directory
CACHE_DIR = "tts_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Hugging Face API settings
API_URL = "https://api-inference.huggingface.co/models/tts_models--en--ljspeech--tacotron2-DDC_ph"
API_TOKEN = os.getenv("HF_TOKEN")
if not API_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables. Please check your .env file.")
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

random.seed(time.time())

def get_random_error_response():
    """
    Returns a random error response from the predefined list.
    """
    return random.choice(ERROR_RESPONSES)

class TTS_Handler(BaseMQTTHandler):
    def __init__(self, topic, main_topic, name):
        super().__init__(topic, main_topic, name)
        pygame.mixer.init()

    def get_cache_path(self, text):
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return os.path.join(CACHE_DIR, f"{text_hash}_childlike.wav")

    def play_audio(self, audio_segment):
        buffer = io.BytesIO()
        audio_segment.export(buffer, format="wav")
        buffer.seek(0)
        pygame.mixer.music.load(buffer)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def text_to_speech(self, text):
        start_time = time.time()
        cached_path = self.get_cache_path(text)
        
        if os.path.exists(cached_path):
            print("Using cached voice")
            final_audio = AudioSegment.from_file(cached_path, format="wav")
        else:
            print("Generating new voice...")
            
            # Generate audio using Hugging Face API
            try:
                print(f"Making API request to: {API_URL}")
                response = requests.post(API_URL, headers=headers, json={"inputs": text})
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                
                if response.status_code != 200:
                    print(f"Error response: {response.text}")
                    raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
                # Save raw audio to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_file.write(response.content)
                    raw_path = temp_file.name
                
                # Load raw audio
                sound = AudioSegment.from_file(raw_path, format="wav")
                
                # Step 1: Childlike pitch (0.13 octaves up)
                octaves = 0.13
                new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
                childlike = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
                childlike = childlike.set_frame_rate(22050)
                
                # Step 2: Slightly faster (5%)
                speed_factor = 1
                faster = childlike._spawn(childlike.raw_data, overrides={
                    "frame_rate": int(childlike.frame_rate * speed_factor)
                }).set_frame_rate(22050)
                
                # Save final voice to cache
                faster.export(cached_path, format="wav")
                os.remove(raw_path)  # Clean up raw file
                final_audio = faster
                
                # Print API response time
                api_time = time.time() - start_time
                print(f"API Response time: {api_time:.2f} seconds")
            except Exception as e:
                print(f"Error in text_to_speech: {e}")
                raise
        
        return final_audio

    def handle_message(self, text):
        """
        Generate TTS audio, apply pitch/speed, cache, and play.
        """
        if not text.strip():
            print("Skipped empty text.")
            return

        try:
            final_audio = self.text_to_speech(text)
            print("Playing voice...")
            self.play_audio(final_audio)
        except Exception as e:
            print(f"Error in handle_message: {e}")

    def execute_main(self, input_data):
        try:
            response = input_data.get("response", get_random_error_response())
            print(f"Speaking: {response}")
            self.handle_message(response)

            # Publish the result
            self.publish_result_default({"response": response})

        except Exception as e:
            print(f"Error processing message: {e}")
            self.publish_result_default({"response": "-1"})

if __name__ == "__main__":
    tts_handler = TTS_Handler("Robot/tts", "Robot/main", "tts")
    tts_handler.start()