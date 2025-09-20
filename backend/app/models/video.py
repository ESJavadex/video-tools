from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranscriptionSegment(BaseModel):
    timestamp: str
    text: str
    start_seconds: float
    end_seconds: Optional[float] = None

class VideoSuggestions(BaseModel):
    title: str
    titles: List[str] = []  # Multiple title options
    description: str
    thumbnail_prompt: str
    highlights: List[TranscriptionSegment]

class VideoTranscriptionRequest(BaseModel):
    file_path: str
    language: str = "es"

class VideoTranscriptionResponse(BaseModel):
    id: str
    original_filename: str
    transcription: List[TranscriptionSegment]
    suggestions: VideoSuggestions
    duration_seconds: float
    processed_at: datetime

class VideoUploadResponse(BaseModel):
    id: str
    filename: str
    file_path: str
    size_mb: float
    uploaded_at: datetime

class RegenerateSuggestionsRequest(BaseModel):
    transcription: List[TranscriptionSegment]
    custom_instructions: Optional[str] = None

class RegenerateSuggestionsResponse(BaseModel):
    titles: List[str]
    description: str
    thumbnail_prompt: str