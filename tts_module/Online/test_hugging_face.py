import os
import hashlib
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play

# Setup cache directory
CACHE_DIR = "tts_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Text to synthesize
text = "Hi there! I'm your little assistant. Let's play!"

# Generate unique filename hash based on text
def get_cache_path(text):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}_childlike.wav")

# Check cache
cached_path = get_cache_path(text)

if os.path.exists(cached_path):
    print("Using cached voice")
    final_audio = AudioSegment.from_file(cached_path, format="wav")
else:
    print("🎤 Generating new voice...")

    # Load the model (runs only once)
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph", progress_bar=False, gpu=False)

    # Temporary file for raw synthesis
    raw_path = get_cache_path(text).replace("_childlike", "_raw")
    tts.tts_to_file(text=text, file_path=raw_path)

    # Load raw audio
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

    # Save final voice to cache
    faster.export(cached_path, format="wav")
    os.remove(raw_path)  # Clean up raw file
    final_audio = faster

# Play the final audio
print("Playing voice...")
play(final_audio)
