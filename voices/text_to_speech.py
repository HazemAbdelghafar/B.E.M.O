import pyttsx3
from gtts import gTTS
import os
import pygame

def initialize_tts_engine():
    try:
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', 170) 
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
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

def download_and_play_speech(engine, text, lang='en'):
    try:
        filename = "temp_speech.mp3"
        
        # Create speech file
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        
        # Play the speech
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.unload() 
        os.remove(filename) 
        

    except Exception as e:
        print(f"Error during speech synthesis: {e}")

if __name__ == "__main__":
    engine = initialize_tts_engine()

    while True:
        text = input("Enter the text you want to hear (or type 'exit' to quit): ")
        if text.lower() == 'exit':
            print("Goodbye!")
            break
        download_and_play_speech(engine, text)
