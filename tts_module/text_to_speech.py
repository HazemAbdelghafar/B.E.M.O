import pyttsx3
from gtts import gTTS
import os
import pygame
from io import BytesIO

CWD = os.path.dirname(os.path.realpath(__file__))


def initialize_tts_engine():
    try:
        engine = pyttsx3.init()
        rate = engine.getProperty("rate")
        engine.setProperty("rate", 170)
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[0].id)
        return engine
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        return None


def text_to_speech(engine, text):
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error during text-to-speech: {e}")
    else:
        print("TTS engine not initialized.")


def play_speech(
    text, lang="en", download=False, download_path=f"{CWD}/speech.mp3"
):
    pygame.mixer.init()

    if download:
        try:
            # Create speech file
            tts = gTTS(text=text, lang=lang)
            tts.save(download_path)
            pygame.mixer.music.load(download_path)
            pygame.mixer.music.play()

            # Wait for the speech to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        except Exception as e:
            print(f"Error during speech synthesis: {e}")

    else:
        try:

            # Create speech file
            tts = gTTS(text=text, lang=lang)
            bytes = BytesIO()
            tts.write_to_fp(bytes)
            bytes.seek(0)
            pygame.mixer.music.load(bytes)
            pygame.mixer.music.play()

            # Wait for the speech to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        except Exception as e:
            print(f"Error during speech synthesis: {e}")


if __name__ == "__main__":
    engine = initialize_tts_engine()

    while True:
        text = input("Enter the text you want to hear (or type 'exit' to quit): ")
        if text.lower() == "exit":
            print("Goodbye!")
            break
        play_speech(text, download=False)
