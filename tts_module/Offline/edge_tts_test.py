import asyncio
import edge_tts
import os
import time
from pathlib import Path

class EdgeTTS:
    def __init__(self):
        # Default voice and settings - optimized for child-like voice
        self.current_voice = 'en-US-JennyNeural'
        self.rate = '-10%'
        self.volume = '+0%'
        self.pitch = '+35Hz'
        
        # Pre-initialize the communicate object for better performance
        self._communicate = edge_tts.Communicate(
            "",
            self.current_voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch
        )

    async def _generate_speech(self, text, output_file):
        """Generate speech using Edge TTS"""
        self._communicate.text = text
        await self._communicate.save(output_file)

    def speak(self, text, output_file):
        """Convert text to speech and save as WAV file"""
        try:
            # Start timing
            start_time = time.time()
            
            # Generate speech
            asyncio.run(self._generate_speech(text, output_file))
            
            # Calculate and print time taken
            end_time = time.time()
            time_taken = end_time - start_time
            print(f"Speech generation took {time_taken:.2f} seconds")
            
            return output_file
        except Exception as e:
            print(f"Error in speech generation: {str(e)}")
            return None

    def set_voice(self, voice_id):
        """Set a specific voice by ID"""
        self.current_voice = voice_id
        self._communicate = edge_tts.Communicate(
            "",
            self.current_voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch
        )

    def set_rate(self, rate_percent):
        """Set speaking rate"""
        self.rate = str(rate_percent)
        self._communicate.rate = self.rate

    def set_volume(self, volume_percent):
        """Set volume"""
        self.volume = str(volume_percent)
        self._communicate.volume = self.volume

    def set_pitch(self, pitch_hz):
        """Set pitch"""
        self.pitch = str(pitch_hz)
        self._communicate.pitch = self.pitch

# Example usage
if __name__ == "__main__":
    tts = EdgeTTS()
    tts.speak("Hello! I am BEEMO and this is the last sound check!", "bemo_intro.wav") 