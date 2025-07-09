import os
from dotenv import load_dotenv

load_dotenv()

"""
Project-wide configuration settings.
"""

WHISPER_MODEL_NAME = "base.en"

GOP_MODEL_NAME = "moxeeeem/wav2vec2-finetuned-pronunciation-correction"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL_NAME = "gemini-1.5-flash-latest"