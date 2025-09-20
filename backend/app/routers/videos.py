from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import os
import shutil
import uuid
import time
import json
from datetime import datetime
from app.models.video import (
    VideoUploadResponse,
    VideoTranscriptionResponse,
    RegenerateSuggestionsRequest,
    RegenerateSuggestionsResponse
)
from app.services.video_processor import VideoProcessor
from app.services.suggestions_service import SuggestionsService
from app.config import get_settings

router = APIRouter(prefix="/api/videos", tags=["videos"])
settings = get_settings()
video_processor = VideoProcessor()
suggestions_service = SuggestionsService()

# Create uploads and analysis directories if they don't exist
os.makedirs(settings.upload_directory, exist_ok=True)
os.makedirs(settings.analysis_directory, exist_ok=True)

def generate_short_id() -> str:
    """Generate a short unique ID for Gemini API (max 40 chars)"""
    # Use timestamp + short UUID to ensure uniqueness and keep under 40 chars
    timestamp = str(int(time.time()))[-8:]  # Last 8 digits of timestamp
    short_uuid = str(uuid.uuid4()).replace('-', '')[:20]  # 20 chars from UUID
    return f"{timestamp}{short_uuid}"  # Total: 28 chars + extension will be under 40

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file for processing"""

    # Validate file
    try:
        video_processor.validate_video_file(file.filename, file.size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate unique filename (short for Gemini API compatibility)
    file_id = generate_short_id()
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(settings.upload_directory, saved_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Get file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    return VideoUploadResponse(
        id=file_id,
        filename=file.filename,
        file_path=file_path,
        size_mb=round(file_size_mb, 2),
        uploaded_at=datetime.utcnow()
    )

@router.post("/transcribe/{video_id}", response_model=VideoTranscriptionResponse)
async def transcribe_video(video_id: str):
    """Process and transcribe an uploaded video"""

    # Find video file
    video_files = [f for f in os.listdir(settings.upload_directory) if f.startswith(video_id)]

    if not video_files:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = os.path.join(settings.upload_directory, video_files[0])

    try:
        # Process video
        result = await video_processor.process_video(file_path, video_files[0])

        # Save analysis result
        save_analysis_result(result, video_files[0])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/process", response_model=VideoTranscriptionResponse)
async def upload_and_process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and immediately process a video file"""

    # Validate file
    try:
        video_processor.validate_video_file(file.filename, file.size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate unique filename (short for Gemini API compatibility)
    file_id = generate_short_id()
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(settings.upload_directory, saved_filename)

    # Debug: log filename length
    print(f"DEBUG: Generated filename: {saved_filename} (length: {len(saved_filename)})")
    print(f"DEBUG: File ID: {file_id} (length: {len(file_id)})")

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Process video
    try:
        result = await video_processor.process_video(file_path, file.filename)

        # Save analysis result
        save_analysis_result(result, file.filename)

        # Clean up file after processing
        background_tasks.add_task(cleanup_file, file_path)

        return result
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

def save_analysis_result(result: VideoTranscriptionResponse, original_filename: str):
    """Save analysis result to analysis_results folder"""
    try:
        # Generate filename with timestamp and original name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean filename for filesystem
        clean_filename = "".join(c for c in original_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_filename = clean_filename.replace(' ', '_')

        # Create analysis filename
        analysis_filename = f"{timestamp}_{clean_filename}_analysis.json"
        analysis_path = os.path.join(settings.analysis_directory, analysis_filename)

        # Convert result to dict for JSON serialization
        analysis_data = {
            "original_filename": original_filename,
            "analysis_id": result.id,
            "processed_at": result.processed_at.isoformat(),
            "duration_seconds": result.duration_seconds,
            "transcription": [seg.dict() for seg in result.transcription],
            "suggestions": result.suggestions.dict()
        }

        # Save to JSON file
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"DEBUG: Analysis saved to: {analysis_path}")

    except Exception as e:
        print(f"WARNING: Failed to save analysis result: {str(e)}")

def cleanup_file(file_path: str):
    """Remove temporary file after processing"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

@router.post("/regenerate-suggestions", response_model=RegenerateSuggestionsResponse)
async def regenerate_suggestions(request: RegenerateSuggestionsRequest):
    """Regenerate suggestions based on transcription with custom instructions"""
    try:
        # Convert Pydantic models to dict for suggestions service
        transcription_dicts = [seg.dict() for seg in request.transcription]

        # Call suggestions service to regenerate suggestions
        result = suggestions_service.regenerate_suggestions(
            transcription=transcription_dicts,
            custom_instructions=request.custom_instructions
        )

        return RegenerateSuggestionsResponse(
            titles=result.get("titles", []),
            description=result.get("description", ""),
            thumbnail_prompt=result.get("thumbnail_prompt", "")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Check if the video service is running"""
    return {"status": "healthy", "service": "video-processor"}