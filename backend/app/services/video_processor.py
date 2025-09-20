import os
import uuid
from datetime import datetime
from typing import Optional
from app.models.video import (
    VideoTranscriptionResponse,
    VideoSuggestions,
    TranscriptionSegment
)
from app.services.whisper_service import WhisperService
from app.services.suggestions_service import SuggestionsService
from app.config import get_settings

class VideoProcessor:
    def __init__(self):
        self.whisper_service = WhisperService(model_name="small")  # Better accuracy for longer videos
        self.suggestions_service = SuggestionsService()
        self.settings = get_settings()

    async def process_video(self, file_path: str, original_filename: str) -> VideoTranscriptionResponse:
        """Process video file and return transcription with suggestions"""

        # Generate unique ID for this processing job
        video_id = str(uuid.uuid4())

        print(f"DEBUG: Starting video processing for file: {file_path}")
        print(f"DEBUG: Original filename: {original_filename}")

        # Step 1: Try local Whisper transcription, fallback to Gemini if needed
        whisper_result = None
        try:
            print(f"DEBUG: Starting local Whisper transcription...")
            whisper_result = self.whisper_service.transcribe_video(file_path, language="es")
            print(f"DEBUG: Whisper transcription completed successfully")
        except Exception as whisper_error:
            print(f"DEBUG: Whisper failed: {str(whisper_error)}")
            print(f"DEBUG: Falling back to Gemini for transcription...")

            # Fallback to old Gemini method
            from app.services.gemini import GeminiService
            gemini_service = GeminiService()

            # Upload video to Gemini
            video_file_name = gemini_service.upload_video(file_path)
            gemini_result = gemini_service.transcribe_video(video_file_name, language="es", original_filename=original_filename)

            # Convert Gemini result to Whisper format
            whisper_result = {
                "transcription": gemini_result.get("transcription", []),
                "duration": 0
            }
            print(f"DEBUG: Gemini fallback transcription completed successfully")

        # Step 2: Generate suggestions with Gemini
        print(f"DEBUG: Generating suggestions with Gemini...")
        suggestions_result = self.suggestions_service.generate_suggestions(
            whisper_result["transcription"],
            original_filename
        )
        print(f"DEBUG: Suggestions generation completed successfully")

        # Parse transcription from Whisper
        transcription_segments = []
        for segment in whisper_result.get("transcription", []):
            transcription_segments.append(TranscriptionSegment(
                timestamp=segment["timestamp"],
                text=segment["text"],
                start_seconds=segment.get("start_seconds", 0),
                end_seconds=segment.get("end_seconds")
            ))

        # Parse highlights from suggestions
        highlights = []
        for highlight in suggestions_result.get("highlights", []):
            highlights.append(TranscriptionSegment(
                timestamp=highlight["timestamp"],
                text=highlight.get("text", ""),
                start_seconds=self._parse_timestamp(highlight["timestamp"])
            ))

        # Create suggestions object
        suggestions = VideoSuggestions(
            title=suggestions_result.get("title", ""),
            description=suggestions_result.get("description", ""),
            thumbnail_prompt=suggestions_result.get("thumbnail_prompt", ""),
            highlights=highlights
        )

        # Use duration from Whisper
        duration = whisper_result.get("duration", 0)
        if not duration and transcription_segments:
            duration = max(seg.start_seconds for seg in transcription_segments)

        return VideoTranscriptionResponse(
            id=video_id,
            original_filename=original_filename,
            transcription=transcription_segments,
            suggestions=suggestions,
            duration_seconds=duration,
            processed_at=datetime.utcnow()
        )

    def _parse_timestamp(self, timestamp: str) -> float:
        """Convert timestamp string to seconds"""
        try:
            parts = timestamp.split(':')
            if len(parts) == 2:  # MM:SS
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        except:
            return 0.0
        return 0.0

    def validate_video_file(self, filename: str, file_size: int) -> bool:
        """Validate video file extension and size"""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.settings.allowed_video_extensions:
            raise ValueError(f"Invalid file type. Allowed: {self.settings.allowed_video_extensions}")

        if file_size > self.settings.max_file_size:
            raise ValueError(f"File too large. Max size: {self.settings.max_file_size / (1024*1024)}MB")

        return True