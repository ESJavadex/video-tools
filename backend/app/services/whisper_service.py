import whisper
import os
import tempfile
import json
from typing import List, Dict, Any, Optional
import ffmpeg
from datetime import timedelta, datetime

class WhisperService:
    def __init__(self, model_name: str = "base", progress_dir: Optional[str] = None):
        """
        Initialize Whisper service with specified model
        Models available: tiny, base, small, medium, large
        - tiny: fastest, least accurate
        - base: good balance (recommended for most uses)
        - small: better accuracy, slower
        - medium/large: best accuracy, much slower
        """
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        print(f"Whisper model {model_name} loaded successfully")

        # Setup progress tracking directory
        self.progress_dir = progress_dir or "analysis_results/transcription_progress"
        os.makedirs(self.progress_dir, exist_ok=True)

    def transcribe_video(self, video_path: str, language: str = "es", video_id: Optional[str] = None, original_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe video file using Whisper with progressive saving
        Returns transcription with timestamps
        """
        print(f"Starting local transcription for: {video_path}")

        # Create progress tracking file
        progress_file = None
        if video_id:
            progress_file = self._create_progress_file(video_id, video_path, original_filename)
            print(f"Progress tracking enabled: {progress_file}")

        try:
            # Update progress: extracting audio
            if progress_file:
                self._update_progress(progress_file, "extracting_audio", 5)

            # Extract audio from video if needed
            audio_path = self._extract_audio(video_path)

            # Update progress: transcribing
            if progress_file:
                self._update_progress(progress_file, "transcribing", 10)

            # Transcribe with Whisper
            print("Running Whisper transcription...")
            result = self.model.transcribe(
                audio_path,
                language=language if language != "es" else "spanish",
                word_timestamps=True,
                verbose=True,
                initial_prompt="Transcribe todo el contenido del video completo, sin omitir nada."
            )

            # IMMEDIATELY save raw result after Whisper completes
            if progress_file:
                self._save_raw_whisper_result(progress_file, result)
                self._update_progress(progress_file, "transcription_complete", 90)
                print(f"✓ RAW Whisper result saved to progress file (backup created)")

            # Clean up temporary audio file if created
            if audio_path != video_path:
                os.remove(audio_path)

            # Format result
            transcription_segments = self._format_segments(result["segments"])

            print(f"Transcription completed! Found {len(transcription_segments)} segments")

            # Save formatted segments
            if progress_file:
                self._save_formatted_segments(progress_file, transcription_segments, result.get("duration", 0))
                self._update_progress(progress_file, "complete", 100)
                print(f"✓ Formatted transcription saved to progress file")

            return {
                "transcription": transcription_segments,
                "language": result.get("language", language),
                "duration": result.get("duration", 0)
            }

        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            if progress_file:
                self._update_progress(progress_file, "failed", 0, error=str(e))
            raise Exception(f"Whisper transcription failed: {str(e)}")

    def _extract_audio(self, video_path: str) -> str:
        """Extract audio from video file or use file directly"""
        try:
            # For audio files, return as-is
            if video_path.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                print(f"Audio file detected, using directly: {video_path}")
                return video_path

            # Try to use the video file directly with Whisper
            # Whisper can handle many video formats natively
            print(f"Video file detected, Whisper will handle directly: {video_path}")
            return video_path

            # TODO: Enable ffmpeg extraction when available
            # if shutil.which('ffmpeg'):
            #     return self._extract_with_ffmpeg(video_path)
            # else:
            #     print("FFmpeg not available, using video file directly")
            #     return video_path

        except Exception as e:
            print(f"Audio handling error: {e}. Using original file...")
            return video_path

    def _extract_with_ffmpeg(self, video_path: str) -> str:
        """Extract audio using ffmpeg (when available)"""
        try:
            # Create temporary audio file
            temp_audio = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.wav',
                prefix='whisper_audio_'
            )
            temp_audio.close()

            print(f"Extracting audio to: {temp_audio.name}")

            # Extract audio using ffmpeg
            (
                ffmpeg
                .input(video_path)
                .output(
                    temp_audio.name,
                    acodec='pcm_s16le',
                    ac=1,  # mono
                    ar='16000'  # 16kHz sample rate
                )
                .overwrite_output()
                .run(quiet=True, capture_stdout=True)
            )

            return temp_audio.name

        except Exception as e:
            print(f"FFmpeg extraction failed: {e}. Using original file...")
            return video_path

    def _format_segments(self, segments: List[Dict]) -> List[Dict[str, Any]]:
        """Format Whisper segments to our standard format"""
        formatted_segments = []

        for segment in segments:
            # Convert seconds to MM:SS format
            start_time = segment.get('start', 0)
            timestamp = self._seconds_to_timestamp(start_time)

            # Clean up text
            text = segment.get('text', '').strip()
            if not text:
                continue

            formatted_segments.append({
                "timestamp": timestamp,
                "text": text,
                "start_seconds": start_time,
                "end_seconds": segment.get('end', start_time + 1)
            })

        return formatted_segments

    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        try:
            td = timedelta(seconds=seconds)
            total_seconds = int(td.total_seconds())
            minutes = total_seconds // 60
            secs = total_seconds % 60
            return f"{minutes:02d}:{secs:02d}"
        except:
            return "00:00"

    def _create_progress_file(self, video_id: str, video_path: str, original_filename: Optional[str]) -> str:
        """Create a progress tracking file for this transcription job"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        progress_filename = f"{timestamp}_{video_id}_progress.json"
        progress_path = os.path.join(self.progress_dir, progress_filename)

        progress_data = {
            "video_id": video_id,
            "video_path": video_path,
            "original_filename": original_filename,
            "started_at": datetime.utcnow().isoformat(),
            "status": "started",
            "progress_percent": 0,
            "stage": "initializing",
            "raw_whisper_result": None,
            "formatted_segments": None,
            "error": None
        }

        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)

        return progress_path

    def _update_progress(self, progress_file: str, stage: str, progress: int, error: Optional[str] = None):
        """Update the progress tracking file"""
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["stage"] = stage
            data["progress_percent"] = progress
            data["last_updated"] = datetime.utcnow().isoformat()

            if error:
                data["status"] = "failed"
                data["error"] = error
            elif stage == "complete":
                data["status"] = "complete"
                data["completed_at"] = datetime.utcnow().isoformat()
            else:
                data["status"] = "in_progress"

            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"WARNING: Could not update progress file: {e}")

    def _save_raw_whisper_result(self, progress_file: str, result: Dict):
        """Save the raw Whisper result immediately after transcription"""
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Save full Whisper result (segments, language, etc.)
            data["raw_whisper_result"] = {
                "segments": result.get("segments", []),
                "language": result.get("language", "unknown"),
                "duration": result.get("duration", 0),
                "text": result.get("text", "")
            }
            data["whisper_completed_at"] = datetime.utcnow().isoformat()

            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ Saved {len(result.get('segments', []))} raw Whisper segments")
        except Exception as e:
            print(f"WARNING: Could not save raw Whisper result: {e}")

    def _save_formatted_segments(self, progress_file: str, segments: List[Dict], duration: float):
        """Save formatted segments to progress file"""
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["formatted_segments"] = segments
            data["duration"] = duration
            data["segment_count"] = len(segments)
            data["formatting_completed_at"] = datetime.utcnow().isoformat()

            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ Saved {len(segments)} formatted segments")
        except Exception as e:
            print(f"WARNING: Could not save formatted segments: {e}")

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the loaded model"""
        return {
            "service": "OpenAI Whisper (Local)",
            "model": getattr(self.model, 'name', 'unknown'),
            "status": "ready"
        }