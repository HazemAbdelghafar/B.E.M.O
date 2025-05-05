import pygame
from TTS.api import TTS
from pydub import AudioSegment
from io import BytesIO
import numpy as np
import time

# Initialize TTS
tts = TTS(model_name="tts_models/en/jenny/jenny", progress_bar=False, gpu=False)

# Your text input
text_input = "Hello, This is a test of my voice. Can you hear me clearly? I can speak fast. like this, Zoom, Or slow. and. calm. like this.I ask questions: What's your favorite color?I make statements: The sky is blue.I show emotion: Wow, That’s amazing!And now, for a tongue twister:fucking fucker fuckers fucking bullshit."

# Measure TTS generation time
start = time.time()

# Generate waveform directly
wav = tts.tts(text=text_input)
sample_rate = tts.synthesizer.output_sample_rate

# Convert list of floats to numpy int16 array
wav_np = np.array(wav, dtype=np.float32)
wav_np = wav_np / np.max(np.abs(wav_np))
wav_int16 = (wav_np * 32767).astype(np.int16)

end = time.time()
print(f"TTS processing time: {end - start:.3f} seconds")

# Convert waveform to AudioSegment
audio = AudioSegment(
    wav_int16.tobytes(),
    frame_rate=sample_rate,
    sample_width=2,
    channels=1
)

# Apply childish pitch effect
childish_audio = audio._spawn(audio.raw_data, overrides={
    "frame_rate": int(audio.frame_rate * 1.05)
}).set_frame_rate(audio.frame_rate)

# Save the modified audio to memory
childish_output_audio = BytesIO()
childish_audio.export(childish_output_audio, format="wav")
childish_output_audio.seek(0)

# Initialize pygame mixer
pygame.mixer.init()

# Load the modified WAV file from memory
sound = pygame.mixer.Sound(file=childish_output_audio)

# Play the sound
sound.play()

# Wait long enough for it to finish playing
pygame.time.wait(int(sound.get_length() * 1000))

print("Done playing.")