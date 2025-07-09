# backend/app/api/v1/endpoints/tts.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from app.services.tts_service import TTSService

router = APIRouter()
tts_service = TTSService()

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"

@router.post(
    "/",
    summary="Generate Speech from Text",
    response_class=StreamingResponse
)
async def generate_speech_endpoint(request: TTSRequest):
    """
    Generate audio from text using the TTS service.
    """
    try:
        audio_bytes = tts_service.generate_speech(request.text, request.voice)
        if audio_bytes:
            return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
