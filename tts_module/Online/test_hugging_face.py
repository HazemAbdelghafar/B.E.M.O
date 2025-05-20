import os
import sys
import io
import hashlib
import pygame
from TTS.api import TTS
from pydub import AudioSegment

# Import your base MQTT handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utilities import BaseMQTTHandler, ERROR_RESPONSES

CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class Handler(BaseMQTTHandler):
    def __init__(self, topic, main_topic, name):
        super().__init__(topic, main_topic, name)
        pygame.mixer.init()
        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph", progress_bar=False, gpu=False)

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

    async def handle_message(self, text):
        """
        Generate TTS audio, apply pitch/speed, cache, and play.
        """
        if not text.strip():
            print("Skipped empty text.")
            return

        cached_path = self.get_cache_path(text)
        if os.path.exists(cached_path):
            print("Using cached voice")
            final_audio = AudioSegment.from_file(cached_path, format="wav")
        else:
            print("Generating new voice...")
            raw_path = cached_path.replace("_childlike", "_raw")
            self.tts.tts_to_file(text=text, file_path=raw_path)
            sound = AudioSegment.from_file(raw_path, format="wav")

            # Step 1: Childlike pitch (0.13 octaves up)
            octaves = 0.13
            new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
            childlike = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
            childlike = childlike.set_frame_rate(22050)

            # Step 2: Slightly faster (5%)
            speed_factor = 1.05
            faster = childlike._spawn(childlike.raw_data, overrides={
                "frame_rate": int(childlike.frame_rate * speed_factor)
            }).set_frame_rate(22050)

            faster.export(cached_path, format="wav")
            os.remove(raw_path)
            final_audio = faster

        print("Playing voice...")
        self.play_audio(final_audio)

if __name__ == "__main__":
    tts_handler = Handler("Robot/tts", "Robot/main", "tts")
    tts_handler.start()