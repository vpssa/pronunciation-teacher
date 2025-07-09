import sys
import os
import google.generativeai as genai
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from app.core.config import GEMINI_API_KEY, LLM_MODEL_NAME

class FeedbackService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")
            
            cls._instance = super(FeedbackService, cls).__new__(cls)
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                
                system_prompt = (
                    "You are a world-class American English pronunciation coach. "
                    "Your feedback is always positive, encouraging, specific, and actionable. "
                    "You focus on the physical aspects of making the sound: tongue position, lip shape, and airflow. "
                    "Keep your advice concise and easy to understand, ideally in 2-3 short sentences. "
                    "Do not start with greetings or filler phrases like 'Certainly!' or 'Here's a tip'. "
                    "Directly provide the tip."
                )
                
                cls._model = genai.GenerativeModel(
                    model_name=LLM_MODEL_NAME,
                    system_instruction=system_prompt
                )
            except Exception as e:
                print(f"Error configuring Gemini API or loading model for FeedbackService: {e}")
                raise RuntimeError(f"Failed to initialize FeedbackService (Gemini): {e}") from e
        return cls._instance

    def get_pronunciation_tip(self, phoneme: str, word: str, reference_text: str) -> str:
        """
        Generates a specific, actionable tip for a mispronounced phoneme using Gemini.
        """
        if not self._model:
            raise Exception("FeedbackService is not initialized.")

        user_prompt = (
            f"I'm practicing the sentence: \"{reference_text}\".\n"
            f"I'm having trouble with the '{phoneme}' sound in the word '{word}'.\n"
            f"Give me a specific tip on how to physically produce the '{phoneme}' sound correctly."
        )

        try:
            response = self._model.generate_content(user_prompt)
            tip = response.text.strip()
            return tip
        except Exception as e:
            return "Sorry, I was unable to generate a tip at this moment."
