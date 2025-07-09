# backend/app/api/v1/endpoints/assessment.py

import string
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from g2p_en import G2p

# --- MODIFIED: Import all three services ---
from app.services.asr_service import ASRService
from app.services.gop_service import GOPService
from app.services.feedback_service import FeedbackService
from app.schemas.assessment_schemas import AssessorResponse, WordAnalysis, PhonemeScore

router = APIRouter()

# --- MODIFIED: Instantiate all services ---
asr_service = ASRService()
gop_service = GOPService()
feedback_service = FeedbackService()
g2p = G2p()

# Define the score below which we generate a tip
FEEDBACK_THRESHOLD = 3.5

def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation.replace("'", "")))
    return text

def _map_phonemes_to_words(text: str, scored_phonemes: List[dict]) -> List[WordAnalysis]:
    words = text.split()
    phoneme_cursor = 0
    word_analyses = []

    for word in words:
        word_phonemes_arpabet = [p for p in g2p(word) if p.strip() and p not in [' ', ',', '.', '!', '?']]
        num_phonemes_in_word = len(word_phonemes_arpabet)
        
        current_word_scores = scored_phonemes[phoneme_cursor : phoneme_cursor + num_phonemes_in_word]
        
        phoneme_scores_for_word = []
        for scored_phoneme in current_word_scores:
            # --- MODIFIED: Logic for getting feedback ---
            feedback = None
            if scored_phoneme['score'] < FEEDBACK_THRESHOLD:
                # If score is low, call the feedback service
                print(f"Score for {scored_phoneme['phoneme']} is low ({scored_phoneme['score']}). Generating tip.")
                feedback = feedback_service.get_pronunciation_tip(
                    phoneme=scored_phoneme['phoneme'],
                    word=word,
                    reference_text=text
                )

            phoneme_scores_for_word.append(
                PhonemeScore(
                    phoneme=scored_phoneme['phoneme'],
                    score=scored_phoneme['score'],
                    feedback_tip=feedback # Add the tip to the response
                )
            )

        word_analyses.append(WordAnalysis(word=word, phonemes=phoneme_scores_for_word))
        phoneme_cursor += num_phonemes_in_word
    
    return word_analyses


@router.post(
    "/",
    response_model=AssessorResponse,
    summary="Assess Pronunciation (Full Pipeline)"
)
async def assess_pronunciation(
    reference_text: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Phase 3: Full Pipeline (Checker, Assessor, Diagnostician).
    """
    try:
        audio_bytes = await audio_file.read()
        
        # Stage 1: The Checker (ASR)
        user_transcript = asr_service.transcribe(audio_bytes)
        normalized_reference = normalize_text(reference_text)
        normalized_transcript = normalize_text(user_transcript)
        is_correct = (normalized_reference == normalized_transcript)
        
        word_analysis_list = []
        if is_correct:
            # Stage 2: The Assessor (GOP)
            print("Transcription correct. Proceeding to phoneme assessment...")
            phoneme_scores = gop_service.get_phoneme_scores(audio_bytes, reference_text)
            
            # Stage 3: The Diagnostician (LLM)
            print("Mapping phonemes and generating feedback for low scores...")
            word_analysis_list = _map_phonemes_to_words(reference_text, phoneme_scores)
        
        return AssessorResponse(
            is_correct=is_correct,
            user_transcript=user_transcript,
            words=word_analysis_list
        )

    except Exception as e:
        import traceback
        print(f"An error occurred during assessment: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))