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
from app.services.openai_service import OpenAIService
from app.config import get_settings

class VideoProcessor:
    def __init__(self):
        self.whisper_service = WhisperService(model_name="small")  # Better accuracy for longer videos
        self.settings = get_settings()

        # Initialize AI service based on provider setting
        if self.settings.ai_provider == "openai":
            print(f"DEBUG: Using OpenAI as AI provider (model: {self.settings.openai_model})")
            self.suggestions_service = OpenAIService(model=self.settings.openai_model)
        else:
            print(f"DEBUG: Using Gemini as AI provider")
            self.suggestions_service = SuggestionsService()

    async def process_video(self, file_path: str, original_filename: str) -> VideoTranscriptionResponse:
        """Process video file and return transcription with suggestions"""

        # Generate unique ID for this processing job
        video_id = str(uuid.uuid4())

        print(f"DEBUG: Starting video processing for file: {file_path}")
        print(f"DEBUG: Original filename: {original_filename}")

        # Step 1: Try local Whisper transcription, fallback to Gemini if needed
        whisper_result = None
        try:
            print(f"DEBUG: Starting local Whisper transcription with progress tracking...")
            whisper_result = self.whisper_service.transcribe_video(
                file_path,
                language="es",
                video_id=video_id,
                original_filename=original_filename
            )
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

        # Parse transcription from Whisper FIRST (before Gemini call)
        transcription_segments = []
        for segment in whisper_result.get("transcription", []):
            transcription_segments.append(TranscriptionSegment(
                timestamp=segment["timestamp"],
                text=segment["text"],
                start_seconds=segment.get("start_seconds", 0),
                end_seconds=segment.get("end_seconds")
            ))

        # Use duration from Whisper
        duration = whisper_result.get("duration", 0)
        if not duration and transcription_segments:
            duration = max(seg.start_seconds for seg in transcription_segments)

        # SAVE TRANSCRIPTION IMMEDIATELY (before Gemini call)
        print(f"DEBUG: Saving transcription before Gemini call...")
        self._save_transcription_backup(video_id, original_filename, transcription_segments, duration)
        print(f"DEBUG: Transcription backup saved successfully")

        # Step 2: Generate suggestions with Gemini (with error recovery)
        print(f"DEBUG: Generating suggestions with Gemini...")
        suggestions_result = None
        try:
            suggestions_result = self.suggestions_service.generate_suggestions(
                whisper_result["transcription"],
                original_filename
            )
            print(f"DEBUG: Suggestions generation completed successfully")
        except Exception as gemini_error:
            print(f"WARNING: Gemini suggestions failed: {str(gemini_error)}")
            print(f"WARNING: Transcription is safe! Returning with default suggestions.")
            # Create default/empty suggestions
            suggestions_result = {
                "title": f"Video: {original_filename}",
                "description": "AI suggestions failed to generate. Please use the regenerate feature to try again with your saved transcription.",
                "thumbnail_prompt": "Video thumbnail",
                "thumbnail_texts": ["MIRA ESTO", "NO TE LO PIERDAS", "INCREÍBLE", "DEBES VERLO", "WOW"],
                "highlights": [],
                "action_items": [],
                "linkedin_post": ""
            }

        # Parse highlights from suggestions (limit to maximum 5)
        highlights = []
        highlights_data = suggestions_result.get("highlights", [])[:5]  # Limit to 5 highlights maximum
        for highlight in highlights_data:
            highlights.append(TranscriptionSegment(
                timestamp=highlight["timestamp"],
                text=highlight.get("text", ""),
                start_seconds=self._parse_timestamp(highlight["timestamp"])
            ))

        # Parse action items from suggestions
        action_items = []
        for item in suggestions_result.get("action_items", []):
            from app.models.video import ActionItem
            action_items.append(ActionItem(
                action=item.get("action", ""),
                context=item.get("context", ""),
                priority=item.get("priority", "media")
            ))

        print(f"DEBUG: Parsed {len(action_items)} action items from suggestions")

        # Create suggestions object
        suggestions = VideoSuggestions(
            title=suggestions_result.get("title", ""),
            description=suggestions_result.get("description", ""),
            thumbnail_prompt=suggestions_result.get("thumbnail_prompt", ""),
            thumbnail_texts=suggestions_result.get("thumbnail_texts", []),
            highlights=highlights,
            action_items=action_items,
            linkedin_post=suggestions_result.get("linkedin_post", "")
        )

        return VideoTranscriptionResponse(
            id=video_id,
            original_filename=original_filename,
            transcription=transcription_segments,
            suggestions=suggestions,
            duration_seconds=duration,
            processed_at=datetime.utcnow()
        )

    def _save_transcription_backup(self, video_id: str, original_filename: str, transcription: list, duration: float):
        """Save transcription backup immediately after Whisper completes"""
        import json

        backup_dir = os.path.join(self.settings.analysis_directory, "transcription_backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_filename = "".join(c for c in original_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_filename = clean_filename.replace(' ', '_')

        backup_filename = f"{timestamp}_{clean_filename}_transcription.json"
        backup_path = os.path.join(backup_dir, backup_filename)

        backup_data = {
            "video_id": video_id,
            "original_filename": original_filename,
            "saved_at": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "transcription": [seg.dict() if hasattr(seg, 'dict') else seg for seg in transcription]
        }

        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        print(f"DEBUG: Transcription backup saved to: {backup_path}")

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