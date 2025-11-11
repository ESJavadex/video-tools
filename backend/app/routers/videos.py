from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
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
    RegenerateSuggestionsResponse,
    ClipGenerationRequest,
    ClipGenerationResponse,
    ProcessedClip,
    TranscriptionSegment
)
from app.services.video_processor import VideoProcessor
from app.services.suggestions_service import SuggestionsService
from app.services.clip_selector_service import analyze_transcript_for_clips
from app.services.video_editing_service import (
    detect_person_location,
    process_clip_suggestion
)
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
        print(f"ERROR: Video processing failed: {str(e)}")
        import traceback
        print(f"ERROR: Full traceback:\n{traceback.format_exc()}")

        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)

        # Provide more helpful error message
        error_detail = f"Processing failed: {str(e)}"
        if "gemini" in str(e).lower() or "api" in str(e).lower():
            error_detail += " (Note: Transcription may have completed but AI suggestions failed. Check logs for details.)"

        raise HTTPException(status_code=500, detail=error_detail)

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
        import traceback
        print(f"ERROR: Regeneration failed with exception: {str(e)}")
        print(f"ERROR: Full traceback:\n{traceback.format_exc()}")

        # Check if it's a Gemini API quota error
        error_message = str(e).lower()
        if "quota" in error_message or "rate" in error_message or "limit" in error_message:
            raise HTTPException(
                status_code=429,
                detail=f"API quota exceeded. Please check your Gemini API credits: {str(e)}"
            )
        elif "api_key" in error_message or "authentication" in error_message:
            raise HTTPException(
                status_code=401,
                detail=f"API authentication failed. Check your GEMINI_API_KEY: {str(e)}"
            )
        else:
            raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")

@router.post("/generate-clips", response_model=ClipGenerationResponse)
async def generate_clips(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    desired_length: int = Form(60),
    max_clips: int = Form(5),
    format_type: str = Form("tiktok")
):
    """
    Generate AI-selected clips from a video

    Args:
        file: Video file to process
        desired_length: Target clip length in seconds (default 60)
        max_clips: Maximum number of clips to generate (default 5)
        format_type: Output format - "tiktok", "instagram", or "youtube-shorts" (default "tiktok")

    Returns:
        ClipGenerationResponse with processed clips and metadata
    """
    start_time = time.time()

    # Validate file
    try:
        video_processor.validate_video_file(file.filename, file.size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate unique filename
    file_id = generate_short_id()
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(settings.upload_directory, saved_filename)

    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    try:
        # Step 1: Process video to get transcription
        print(f"Processing video: {file.filename}")
        result = await video_processor.process_video(file_path, file.filename)

        # Step 2: Analyze transcript to find best moments for clips
        print(f"Analyzing transcript for {max_clips} clip suggestions...")
        clip_suggestions = analyze_transcript_for_clips(
            transcription=result.transcription,
            desired_length=desired_length,
            max_clips=max_clips
        )

        if not clip_suggestions:
            raise HTTPException(
                status_code=500,
                detail="Could not generate clip suggestions. Please try with a different video or settings."
            )

        print(f"Found {len(clip_suggestions)} clip suggestions")

        # Step 3: Detect person location in video (for smart cropping)
        print("Detecting person location in video...")
        person_info = detect_person_location(file_path)

        if person_info:
            print(f"Person detected at ({person_info.x}, {person_info.y}) with confidence {person_info.confidence:.2f}")
        else:
            print("No person detected, using default crop positioning")

        # Step 4: Process each clip suggestion
        clips_dir = os.path.join(settings.upload_directory, "clips", file_id)
        os.makedirs(clips_dir, exist_ok=True)

        processed_clips = []

        for i, clip_suggestion in enumerate(clip_suggestions):
            print(f"Processing clip {i + 1}/{len(clip_suggestions)}: {clip_suggestion.start_time}s - {clip_suggestion.end_time}s")

            clip_info = process_clip_suggestion(
                video_path=file_path,
                clip=clip_suggestion,
                output_dir=clips_dir,
                clip_index=i,
                person_info=person_info,
                format_type=format_type
            )

            if clip_info:
                processed_clip = ProcessedClip(
                    clip_id=f"{file_id}_clip_{i + 1}",
                    suggestion=clip_suggestion,
                    file_path=clip_info["file_path"],
                    file_size_mb=clip_info["file_size_mb"],
                    resolution=clip_info["resolution"],
                    person_detection=person_info
                )
                processed_clips.append(processed_clip)
                print(f"Clip {i + 1} processed successfully: {clip_info['file_size_mb']}MB")
            else:
                print(f"Warning: Failed to process clip {i + 1}")

        if not processed_clips:
            raise HTTPException(
                status_code=500,
                detail="Failed to process any clips. Please check video format and try again."
            )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Clean up original video file
        background_tasks.add_task(cleanup_file, file_path)

        print(f"Clip generation complete: {len(processed_clips)} clips in {processing_time:.2f}s")

        return ClipGenerationResponse(
            clips=processed_clips,
            total_clips=len(processed_clips),
            processing_time_seconds=round(processing_time, 2),
            generated_at=datetime.utcnow()
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Error generating clips: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Clip generation failed: {str(e)}")


@router.get("/analyses")
async def list_analyses():
    """List all saved analysis results"""
    try:
        analyses = []

        # Check if analysis directory exists
        if not os.path.exists(settings.analysis_directory):
            return {"analyses": []}

        # List all JSON files in analysis directory
        for filename in os.listdir(settings.analysis_directory):
            if filename.endswith("_analysis.json"):
                file_path = os.path.join(settings.analysis_directory, filename)

                # Read file to get metadata
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    analyses.append({
                        "filename": filename,
                        "original_filename": data.get("original_filename", "Unknown"),
                        "analysis_id": data.get("analysis_id", ""),
                        "processed_at": data.get("processed_at", ""),
                        "duration_seconds": data.get("duration_seconds", 0),
                        "file_size_bytes": os.path.getsize(file_path)
                    })
                except Exception as e:
                    print(f"WARNING: Could not read analysis file {filename}: {str(e)}")
                    continue

        # Sort by processed_at descending (most recent first)
        analyses.sort(key=lambda x: x["processed_at"], reverse=True)

        return {"analyses": analyses}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list analyses: {str(e)}")


@router.get("/analyses/{filename}")
async def load_analysis(filename: str):
    """Load a specific analysis result by filename"""
    try:
        # Security: ensure filename only contains safe characters
        if not filename.endswith("_analysis.json") or ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        file_path = os.path.join(settings.analysis_directory, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Read and return analysis data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to VideoTranscriptionResponse format
        transcription = [TranscriptionSegment(**seg) for seg in data["transcription"]]

        from app.models.video import VideoSuggestions
        suggestions = VideoSuggestions(**data["suggestions"])

        response = VideoTranscriptionResponse(
            id=data["analysis_id"],
            original_filename=data["original_filename"],
            processed_at=datetime.fromisoformat(data["processed_at"]),
            duration_seconds=data["duration_seconds"],
            transcription=transcription,
            suggestions=suggestions
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load analysis: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if the video service is running"""
    return {"status": "healthy", "service": "video-processor"}


@router.get("/gemini-status")
async def check_gemini_status():
    """Check Gemini API connection and status"""
    try:
        import google.generativeai as genai
        from app.config import get_settings

        settings = get_settings()

        # Check if API key is configured
        if not settings.gemini_api_key or settings.gemini_api_key == "":
            return {
                "status": "error",
                "message": "GEMINI_API_KEY not configured in .env file"
            }

        # Try to list models to verify API key works
        genai.configure(api_key=settings.gemini_api_key)
        models = list(genai.list_models())

        return {
            "status": "online",
            "message": "Gemini API is working",
            "api_key_prefix": settings.gemini_api_key[:10] + "..." if len(settings.gemini_api_key) > 10 else "***",
            "models_available": len(models)
        }

    except Exception as e:
        error_str = str(e)

        # Check for common error types
        if "API_KEY_INVALID" in error_str or "invalid" in error_str.lower():
            status_msg = "Invalid API key"
        elif "quota" in error_str.lower() or "limit" in error_str.lower():
            status_msg = "API quota exceeded or rate limited"
        elif "permission" in error_str.lower():
            status_msg = "Permission denied - check API key permissions"
        else:
            status_msg = f"API error: {error_str}"

        return {
            "status": "error",
            "message": status_msg,
            "error": error_str
        }