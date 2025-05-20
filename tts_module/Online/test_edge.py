import os
import sys
import io
import pygame
import random
import time
import asyncio
import edge_tts

# Import your base MQTT handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utilities import BaseMQTTHandler, ERROR_RESPONSES

# Error responses
random.seed(time.time())


def get_random_error_response():
    """
    Returns a random error response from the predefined list.
    """
    return random.choice(ERROR_RESPONSES)


class Handler(BaseMQTTHandler):
    def __init__(self, topic, main_topic, name):
        super().__init__(topic, main_topic, name)
        pygame.mixer.init()

    async def generate_speech(self, text):
        """
        Generate TTS audio using edge-tts and return it as a BytesIO object.
        """
        communicate = edge_tts.Communicate(
            text, voice="en-US-AriaNeural"
        )  # You can change voice here!
        audio_stream = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])

        audio_stream.seek(0)
        return audio_stream

    def execute_main(self, input_data):
        try:
            response = input_data.get("response", get_random_error_response())
            print(f"Speaking: {response}")

            # Generate speech asynchronously
            audio_fp = asyncio.run(self.generate_speech(response))

            # Load and play
            pygame.mixer.music.load(audio_fp)
            pygame.mixer.music.play()

            # Wait until playback finishes
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Publish the result
            self.publish_result_default({"response": response})

        except Exception as e:
            print(f"Error processing message: {e}")
            self.publish_result_default({"response": "-1"})


if __name__ == "__main__":
    tts_handler = Handler("Robot/tts", "Robot/main", "tts")
    tts_handler.start()
