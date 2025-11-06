from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranscriptionSegment(BaseModel):
    timestamp: str
    text: str
    start_seconds: float
    end_seconds: Optional[float] = None

class ActionItem(BaseModel):
    action: str
    context: str
    priority: str  # "alta", "media", "baja"

class VideoSuggestions(BaseModel):
    title: str
    titles: List[str] = []  # Multiple title options
    description: str
    thumbnail_prompt: str
    highlights: List[TranscriptionSegment]
    action_items: List[ActionItem] = []

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

class ClipSuggestion(BaseModel):
    """AI-suggested video clip with engagement analysis"""
    start_time: float  # seconds
    end_time: float    # seconds
    duration: float    # seconds
    reason: str        # Why this clip is engaging
    hook_text: str     # The key phrase/moment
    engagement_score: float  # 0-10 score
    transcript_preview: str  # First few words of the clip

class PersonDetectionInfo(BaseModel):
    """Information about detected person location in video"""
    face_detected: bool
    x: int  # Top-left x coordinate
    y: int  # Top-left y coordinate
    width: int
    height: int
    confidence: float

class ClipGenerationRequest(BaseModel):
    """Request for generating video clips"""
    video_id: Optional[str] = None  # Reference to already processed video
    desired_length: int = 60  # Target clip length in seconds (default 60)
    max_clips: int = 5  # Maximum number of clip suggestions
    format_type: str = "tiktok"  # "tiktok", "instagram", "youtube-shorts"

class ProcessedClip(BaseModel):
    """Information about a processed video clip"""
    clip_id: str
    suggestion: ClipSuggestion
    file_path: str
    file_size_mb: float
    resolution: str  # e.g., "1080x1920" for TikTok
    person_detection: Optional[PersonDetectionInfo] = None

class ClipGenerationResponse(BaseModel):
    """Response containing generated clips and metadata"""
    clips: List[ProcessedClip]
    total_clips: int
    processing_time_seconds: float
    generated_at: datetime