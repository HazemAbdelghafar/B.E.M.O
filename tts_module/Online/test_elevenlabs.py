import time
import tempfile
import os
import pygame
from elevenlabs import generate, set_api_key
import hashlib
import json

# Set your ElevenLabs API key
# You can get it from https://elevenlabs.io
ELEVENLABS_API_KEY = "sk_5b0f4ed6168d33823a6aa64cea4d026280fc1b46fff5ec49"
set_api_key(ELEVENLABS_API_KEY)

# Initialize pygame mixer
pygame.mixer.init()

# Cache directory
CACHE_DIR = "tts_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_cache_path(text, voice_name):
    """Generate a cache file path based on text and voice"""
    # Create a unique hash for the text and voice
    text_hash = hashlib.md5(f"{text}_{voice_name}".encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")

def text_to_speech(text, voice_name="Yumi"):
    try:
        # Start timing
        start_time = time.time()
        
        # Check cache first
        cache_path = get_cache_path(text, voice_name)
        if os.path.exists(cache_path):
            print("Using cached audio...")
            audio = open(cache_path, 'rb').read()
        else:
            print("Generating new audio...")
            # Generate audio with optimized settings
            audio = generate(
                text=text,
                voice=voice_name,
                model="eleven_monolingual_v1"
            )
            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(audio)
        
        # Calculate API time
        api_time = time.time() - start_time
        print(f"Response time: {api_time:.2f} seconds")
        
        # Create a temporary file that won't be deleted automatically
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_filename = temp_file.name
        temp_file.write(audio)
        temp_file.close()
        
        try:
            # Play the audio using pygame
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        finally:
            # Clean up the temporary file after playback
            try:
                os.unlink(temp_filename)
            except:
                pass
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():    
    # Common phrases for testing
    phrases = [
        "Hello!",
        "How are you?",
        "Nice to meet you!",
        "What can I do for you?",
        "I'm here to help!"
    ]
    
    print("Testing TTS...")
    for phrase in phrases:
        print(f"\nTesting phrase: {phrase}")
        text_to_speech(phrase)
        time.sleep(1)  # Small pause between phrases

if __name__ == "__main__":
    main()
