"""
Video Editing Service - FFmpeg-based video processing for TikTok format clips
Handles person detection, smart cropping, and clip extraction
"""

import os
import cv2
import ffmpeg
import numpy as np
from typing import Optional, Tuple
from app.models.video import PersonDetectionInfo, ClipSuggestion

def detect_person_location(video_path: str, sample_frames: int = 10) -> Optional[PersonDetectionInfo]:
    """
    Detect person/face location in video using OpenCV

    Args:
        video_path: Path to the video file
        sample_frames: Number of frames to sample for detection (default 10)

    Returns:
        PersonDetectionInfo with detected face location, or None if no face detected
    """
    try:
        # Load OpenCV's pre-trained Haar Cascade face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return None

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, total_frames // sample_frames)

        detected_faces = []

        # Sample frames throughout the video
        for i in range(sample_frames):
            frame_number = min(i * frame_interval, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if not ret:
                continue

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            # Store detected faces with confidence based on size
            for (x, y, w, h) in faces:
                # Larger faces are generally more confident detections
                confidence = min(1.0, (w * h) / (frame.shape[0] * frame.shape[1]) * 10)
                detected_faces.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': float(confidence)
                })

        cap.release()

        if not detected_faces:
            return None

        # Use the most confident detection (or average location)
        best_face = max(detected_faces, key=lambda f: f['confidence'])

        return PersonDetectionInfo(
            face_detected=True,
            x=best_face['x'],
            y=best_face['y'],
            width=best_face['width'],
            height=best_face['height'],
            confidence=best_face['confidence']
        )

    except Exception as e:
        print(f"Error detecting person: {str(e)}")
        return None


def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """
    Get video width and height

    Args:
        video_path: Path to the video file

    Returns:
        Tuple of (width, height)
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        return width, height
    except Exception as e:
        print(f"Error getting video dimensions: {str(e)}")
        return 1920, 1080  # Default fallback


def calculate_tiktok_crop(
    video_width: int,
    video_height: int,
    person_info: Optional[PersonDetectionInfo] = None,
    screen_percentage: float = 0.7
) -> Tuple[int, int, int, int]:
    """
    Calculate crop coordinates for TikTok format (9:16 aspect ratio)
    with smart positioning based on person location

    Args:
        video_width: Original video width
        video_height: Original video height
        person_info: Detected person location (optional)
        screen_percentage: Percentage of frame for screen content (default 0.7 = 70%)

    Returns:
        Tuple of (crop_x, crop_y, crop_width, crop_height)
    """
    # TikTok aspect ratio: 9:16 (vertical)
    target_aspect = 9 / 16

    # Calculate target dimensions
    # We want the full height, then calculate width based on aspect ratio
    crop_height = video_height
    crop_width = int(crop_height * target_aspect)

    # Ensure crop_width doesn't exceed video width
    if crop_width > video_width:
        crop_width = video_width
        crop_height = int(crop_width / target_aspect)

    # Determine horizontal position
    # For screen recordings with person webcam overlay:
    # - Webcam is usually in a CORNER (small overlay, typically 200-400px)
    # - Main screen content is the primary focus
    # - For TikTok vertical format, we want to show BOTH person AND screen
    #
    # STRATEGY: Always crop from LEFT (x=0) for screen recordings
    # This ensures we capture:
    # 1. Person webcam overlay (if in bottom-left)
    # 2. Left portion of screen content (most important content)
    # 3. Natural viewing experience (left-to-right reading)

    if person_info and person_info.face_detected:
        # Person detected - crop from left to include person + screen
        crop_x = 0
        print(f"DEBUG: Person detected at ({person_info.x}, {person_info.y}) - cropping from LEFT")
    else:
        # No person detected - still crop from left for screen content
        crop_x = 0
        print("DEBUG: No person detected - cropping from LEFT for screen content")

    # Vertical position (usually centered)
    crop_y = (video_height - crop_height) // 2

    # Ensure coordinates are within bounds
    crop_x = max(0, min(crop_x, video_width - crop_width))
    crop_y = max(0, min(crop_y, video_height - crop_height))

    return crop_x, crop_y, crop_width, crop_height


def extract_and_crop_clip(
    video_path: str,
    output_path: str,
    start_time: float,
    end_time: float,
    person_info: Optional[PersonDetectionInfo] = None,
    format_type: str = "tiktok"
) -> bool:
    """
    Extract clip from video and crop to specified format
    For screen recordings: positions screen at TOP and person at BOTTOM

    Args:
        video_path: Path to source video
        output_path: Path for output clip
        start_time: Clip start time in seconds
        end_time: Clip end time in seconds
        person_info: Detected person location for smart cropping
        format_type: Output format ("tiktok", "instagram", "youtube-shorts")

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get video dimensions
        width, height = get_video_dimensions(video_path)

        # Calculate horizontal crop coordinates (from left)
        crop_x, crop_y, crop_width, crop_height = calculate_tiktok_crop(
            width, height, person_info
        )

        # Build ffmpeg command
        input_stream = ffmpeg.input(video_path, ss=start_time, t=end_time - start_time)

        # Step 1: Crop horizontally (from left to include person + screen)
        video = input_stream.video.filter('crop', crop_width, crop_height, crop_x, crop_y)

        # Step 2: Scale to exactly 1080x1920 for TikTok format
        # Using 'force_original_aspect_ratio=decrease' ensures we don't exceed bounds
        # Then pad with black bars if needed
        if format_type in ["tiktok", "instagram", "youtube-shorts"]:
            # Scale to fit within 1080x1920, maintaining aspect ratio
            video = video.filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
            # Pad to exact 1080x1920 with black bars (centered)
            video = video.filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2', color='black')
        else:
            # Fallback for other formats
            video = video.filter('scale', 1080, 1920)

        # Output with audio
        output = ffmpeg.output(
            video,
            input_stream.audio,
            output_path,
            vcodec='libx264',
            acodec='aac',
            video_bitrate='5000k',
            audio_bitrate='192k',
            **{'preset': 'medium', 'crf': 23}
        )

        # Run ffmpeg (overwrite output file if exists)
        ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return True

    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Error extracting clip: {str(e)}")
        return False


def get_clip_file_size(file_path: str) -> float:
    """
    Get file size in megabytes

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except Exception as e:
        print(f"Error getting file size: {str(e)}")
        return 0.0


def process_clip_suggestion(
    video_path: str,
    clip: ClipSuggestion,
    output_dir: str,
    clip_index: int,
    person_info: Optional[PersonDetectionInfo] = None,
    format_type: str = "tiktok"
) -> Optional[dict]:
    """
    Process a single clip suggestion into a video file

    Args:
        video_path: Source video path
        clip: ClipSuggestion with timing information
        output_dir: Directory for output clips
        clip_index: Index for naming the output file
        person_info: Detected person location
        format_type: Output format type

    Returns:
        Dict with clip info (file_path, size_mb, resolution) or None on error
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        output_filename = f"clip_{clip_index + 1}_{int(clip.start_time)}s-{int(clip.end_time)}s.mp4"
        output_path = os.path.join(output_dir, output_filename)

        # Extract and crop clip
        success = extract_and_crop_clip(
            video_path,
            output_path,
            clip.start_time,
            clip.end_time,
            person_info,
            format_type
        )

        if not success:
            return None

        # Get clip metadata
        file_size_mb = get_clip_file_size(output_path)

        # Resolution based on format
        resolution = "1080x1920" if format_type in ["tiktok", "instagram", "youtube-shorts"] else "1080x1920"

        return {
            "file_path": output_path,
            "file_size_mb": file_size_mb,
            "resolution": resolution
        }

    except Exception as e:
        print(f"Error processing clip: {str(e)}")
        return None
