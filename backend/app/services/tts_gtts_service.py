# backend/app/services/tts_service.py

import sys
import os
from gtts import gTTS
import io

# --- Path Setup ---
# This part is kept for structural consistency with your project.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TTSService:
    """
    A Singleton service for generating speech using the free gTTS library.
    This implementation requires an internet connection but no API key.
    """
    _instance = None
    # gTTS is stateless, so we don't need a persistent client/engine object.

    def __new__(cls):
        # The singleton pattern is kept to maintain a consistent API.
        if cls._instance is None:
            cls._instance = super(TTSService, cls).__new__(cls)
        return cls._instance

    def generate_speech(self, text: str, voice: str = "en"):
        """
        Generates speech from text using the gTTS (Google Text-to-Speech) library.

        Args:
            text (str): The input text to convert to speech.
            voice (str): The language code for the voice (e.g., 'en' for English,
                         'fr' for French, 'es' for Spanish).

        Returns:
            bytes: The raw MP3 audio data, or None on failure.
        """
        if not self._instance:
            raise Exception("TTSService is not initialized.")

        try:
            # Create an in-memory binary file object.
            mp3_in_memory_file = io.BytesIO()

            # Create the gTTS object. 'lang' is the key parameter.
            tts_engine = gTTS(text=text, lang=voice, slow=False)

            # Write the generated MP3 audio into the in-memory file.
            tts_engine.write_to_fp(mp3_in_memory_file)
            
            # Go to the beginning of the in-memory file to read it.
            mp3_in_memory_file.seek(0)
            
            return mp3_in_memory_file.read()

        except Exception as e:
            # Catches potential network errors or other gTTS issues.
            print(f"Error generating speech with gTTS: {e}")
            return None