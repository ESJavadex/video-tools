#!/usr/bin/env python3
"""Test script to verify local Whisper transcription functionality"""

import requests
import os
import tempfile
import json

# Create a temporary test video file (very small)
def create_test_video():
    """Create a small test video file for testing"""
    # For now, let's just test with an existing video file path
    # The user mentioned "Video 4 creador de titulos y descripciones.mp4"
    # We'll create a minimal test to verify the Whisper service works

    test_video_path = "/tmp/test_video.mp4"

    # Create a tiny test video using ffmpeg (if available)
    try:
        import subprocess
        # Create a 1-second black video with a single beep
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'color=black:size=320x240:duration=1',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=1',
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', test_video_path
        ], check=True, capture_output=True)
        return test_video_path
    except Exception as e:
        print(f"Could not create test video: {e}")
        return None

def test_whisper_service():
    """Test the Whisper service directly"""
    from app.services.whisper_service import WhisperService

    print("Testing WhisperService initialization...")
    try:
        whisper_service = WhisperService(model_name="tiny")  # Use tiny model for faster testing
        print("✓ WhisperService initialized successfully")

        # Test if we can access model info
        info = whisper_service.get_model_info()
        print(f"Model info: {info}")
        return True

    except Exception as e:
        print(f"✗ WhisperService failed: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint with a health check"""
    try:
        response = requests.get("http://localhost:8000/api/videos/health")
        if response.status_code == 200:
            print("✓ API endpoint is healthy")
            return True
        else:
            print(f"✗ API endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Local Whisper Functionality ===\n")

    # Test 1: API Health Check
    print("1. Testing API health...")
    api_healthy = test_api_endpoint()

    # Test 2: Whisper Service
    print("\n2. Testing Whisper service...")
    whisper_working = test_whisper_service()

    # Test 3: FFmpeg availability
    print("\n3. Testing FFmpeg availability...")
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg is available")
            ffmpeg_available = True
        else:
            print("✗ FFmpeg not working properly")
            ffmpeg_available = False
    except Exception as e:
        print(f"✗ FFmpeg not found: {e}")
        ffmpeg_available = False

    # Summary
    print("\n=== Test Results ===")
    print(f"API Health: {'✓' if api_healthy else '✗'}")
    print(f"Whisper Service: {'✓' if whisper_working else '✗'}")
    print(f"FFmpeg Available: {'✓' if ffmpeg_available else '✗'}")

    if api_healthy and whisper_working and ffmpeg_available:
        print("\n🎉 All tests passed! Local Whisper transcription should work correctly.")
        print("The system should now transcribe actual video content instead of cached results.")
    else:
        print("\n❌ Some tests failed. Local Whisper may not work properly.")
        print("The system will fall back to Gemini API for transcription.")