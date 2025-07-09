# backend/app/schemas/assessment_schemas.py

from pydantic import BaseModel
from typing import List, Optional

# ... (CheckerResponse remains the same) ...
class CheckerResponse(BaseModel):
    is_correct: bool
    user_transcript: str

# --- MODIFIED: Add optional feedback_tip field ---
class PhonemeScore(BaseModel):
    """Defines the score and optional feedback for a single phoneme."""
    phoneme: str
    score: float
    feedback_tip: Optional[str] = None # The new field for Phase 3

class WordAnalysis(BaseModel):
    """Defines the analysis for a single word, including its phonemes."""
    word: str
    phonemes: List[PhonemeScore]

class AssessorResponse(BaseModel):
    """Defines the full response structure for a successful assessment."""
    is_correct: bool
    user_transcript: str
    words: List[WordAnalysis]

# --- Verification Print Statement ---
if __name__ == "__main__":
    print("--- Verifying assessment_schemas.py for Phase 3 ---")
    print("\nTesting AssessorResponse with feedback_tip:")
    
    sample_response = AssessorResponse(
        is_correct=True,
        user_transcript="I saw a ship",
        words=[
            WordAnalysis(word="I", phonemes=[PhonemeScore(phoneme="AY1", score=4.8)]),
            WordAnalysis(
                word="ship",
                phonemes=[
                    PhonemeScore(phoneme="SH", score=4.6),
                    PhonemeScore(
                        phoneme="IH1",
                        score=2.1,
                        feedback_tip="To make the 'ih' sound, ensure your tongue is high and towards the front..."
                    ),
                    PhonemeScore(phoneme="P", score=4.7)
                ]
            )
        ]
    )
    
    try:
        print(sample_response.model_dump_json(indent=2))
        print("\nValidation successful for AssessorResponse with feedback.")
    except AttributeError:
        print(sample_response.json(indent=2))
        print("\nValidation successful for AssessorResponse with feedback.")

    print("\nSchema verification PASSED.")