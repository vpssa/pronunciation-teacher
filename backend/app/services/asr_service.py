# backend/app/services/asr_service.py

import io
import os
import sys
import torch
import whisper
import tempfile

# Add the project root to the Python path
# This allows us to import from the 'app' module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core.config import WHISPER_MODEL_NAME

class ASRService:
    _instance = None
    _model = None

    # Singleton pattern to ensure only one model instance is loaded
    def __new__(cls):
        if cls._instance is None:
            print("Creating ASRService instance and loading Whisper model...")
            cls._instance = super(ASRService, cls).__new__(cls)
            try:
                # Load the Whisper model
                cls._model = whisper.load_model(WHISPER_MODEL_NAME)
                print(f"Whisper model '{WHISPER_MODEL_NAME}' loaded successfully.")
                # Check for GPU and move model if available
                if torch.cuda.is_available():
                    cls._model = cls._model.to('cuda')
                    print("Model moved to GPU.")
            except Exception as e:
                print(f"Error loading Whisper model: {e}")
                raise RuntimeError(f"Failed to load ASR model: {e}") from e
        return cls._instance

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribes the given audio bytes into text.
        """
        if self._model is None:
            raise Exception("Whisper model is not loaded.")

        print("Transcribing audio...")
        
        # Whisper expects a file path, so we write the audio bytes to a temporary file.
        temp_audio_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_bytes)
                temp_audio_path = temp_audio_file.name

            # Transcribe the audio file
            result = self._model.transcribe(temp_audio_path, fp16=torch.cuda.is_available())
            
            transcribed_text = result.get("text", "").strip()
            print(f"Transcription complete. Result: '{transcribed_text}'")
            return transcribed_text
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            raise
        finally:
            # Clean up the temporary file
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)


# --- Verification Print Statement ---
# This block allows us to test the service directly.
if __name__ == "__main__":
    print("--- Verifying ASRService ---")
    