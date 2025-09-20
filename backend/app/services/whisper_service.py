import whisper
import os
import tempfile
from typing import List, Dict, Any
import ffmpeg
from datetime import timedelta

class WhisperService:
    def __init__(self, model_name: str = "base"):
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

    def transcribe_video(self, video_path: str, language: str = "es") -> Dict[str, Any]:
        """
        Transcribe video file using Whisper
        Returns transcription with timestamps
        """
        print(f"Starting local transcription for: {video_path}")

        try:
            # Extract audio from video if needed
            audio_path = self._extract_audio(video_path)

            # Transcribe with Whisper
            print("Running Whisper transcription...")
            result = self.model.transcribe(
                audio_path,
                language=language if language != "es" else "spanish",
                word_timestamps=True,
                verbose=True,
                initial_prompt="Transcribe todo el contenido del video completo, sin omitir nada."
            )

            # Clean up temporary audio file if created
            if audio_path != video_path:
                os.remove(audio_path)

            # Format result
            transcription_segments = self._format_segments(result["segments"])

            print(f"Transcription completed! Found {len(transcription_segments)} segments")

            return {
                "transcription": transcription_segments,
                "language": result.get("language", language),
                "duration": result.get("duration", 0)
            }

        except Exception as e:
            print(f"Error during transcription: {str(e)}")
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

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the loaded model"""
        return {
            "service": "OpenAI Whisper (Local)",
            "model": getattr(self.model, 'name', 'unknown'),
            "status": "ready"
        }