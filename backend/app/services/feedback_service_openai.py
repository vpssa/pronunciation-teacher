import sys
import os
from openai import OpenAI
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from app.core.config import OPENAI_API_KEY, LLM_MODEL_NAME

class FeedbackService:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
            
            cls._instance = super(FeedbackService, cls).__new__(cls)
            try:
                cls._client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception as e:
                print(f"Error initializing OpenAI client for FeedbackService: {e}")
                raise RuntimeError(f"Failed to initialize FeedbackService (OpenAI): {e}") from e
        return cls._instance

    def get_pronunciation_tip(self, phoneme: str, word: str, reference_text: str) -> str:
        """
        Generates a specific, actionable tip for a mispronounced phoneme.
        """
        if not self._client:
            raise Exception("FeedbackService is not initialized.")

        system_prompt = (
            "You are a world-class American English pronunciation coach. "
            "Your feedback is always positive, encouraging, specific, and actionable. "
            "You focus on the physical aspects of making the sound: tongue position, lip shape, and airflow. "
            "Keep your advice concise and easy to understand, ideally in 2-3 short sentences. "
            "Do not start with greetings or filler phrases like 'Certainly!' or 'Here's a tip'. "
            "Directly provide the tip."
        )

        user_prompt = (
            f"I'm practicing the sentence: \"{reference_text}\".\n"
            f"I'm having trouble with the '{phoneme}' sound in the word '{word}'.\n"
            f"Give me a specific tip on how to physically produce the '{phoneme}' sound correctly."
        )

        try:
            response = self._client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=100,
            )
            tip = response.choices[0].message.content.strip()
            return tip
        except Exception as e:
            return "Sorry, I was unable to generate a tip at this moment."
