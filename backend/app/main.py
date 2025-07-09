from fastapi import FastAPI
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pronunciation Teacher API",
    description="An API to assess English pronunciation using a three-stage feedback pipeline.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"])

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Pronunciation Teacher API is running"}

