
import sys
import os
from openai import OpenAI
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from app.core.config import OPENAI_API_KEY

class TTSService:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
            
            cls._instance = super(TTSService, cls).__new__(cls)
            try:
                cls._client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception as e:
                print(f"Error initializing OpenAI client for TTSService: {e}")
                raise RuntimeError(f"Failed to initialize TTSService: {e}") from e
        return cls._instance

    def generate_speech(self, text: str, voice: str = "alloy"):
        """
        Generates speech from text using OpenAI's TTS API.
        """
        if not self._client:
            raise Exception("TTSService is not initialized.")

        try:
            response = self._client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            return response.read()
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
