# backend/app/api/v1/api.py

from fastapi import APIRouter

from app.api.v1.endpoints import assessment, tts_gtts

# This is the main router for the v1 API.
# It will include all the individual endpoint routers.
api_router = APIRouter()

# Include the assessment router
# All routes from assessment.py will now be prefixed with '/assessment'
# and will be tagged as 'Assessment' in the OpenAPI docs.
api_router.include_router(
    assessment.router,
    prefix="/assessment",
    tags=["Assessment"]
)

# Include the TTS router
api_router.include_router(
    tts_gtts.router,
    prefix="/tts",
    tags=["TTS"]
)

# --- Verification Print Statement ---
# This print statement helps us confirm that this file is being loaded
# when the application starts up.
print("--- Loading v1 API Router (api.py) ---")
print("Included assessment router under /assessment prefix.")
print("Included tts router under /tts prefix.")