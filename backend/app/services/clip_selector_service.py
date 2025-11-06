"""
Clip Selector Service - AI-powered video clip selection using Gemini
Analyzes transcription to find the most engaging moments for short-form content
"""

import google.generativeai as genai
import json
import re
from typing import List
from app.config import get_settings
from app.models.video import TranscriptionSegment, ClipSuggestion

# Configure Gemini
settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

def analyze_transcript_for_clips(
    transcription: List[TranscriptionSegment],
    desired_length: int = 60,
    max_clips: int = 5
) -> List[ClipSuggestion]:
    """
    Analyze video transcription to find the best moments for short clips

    Args:
        transcription: List of transcription segments with timestamps
        desired_length: Target length for each clip in seconds (default 60)
        max_clips: Maximum number of clip suggestions to generate (default 5)

    Returns:
        List of ClipSuggestion objects with engagement analysis
    """

    # Convert transcription segments to text with timestamps
    transcript_text = "\n".join([
        f"[{seg.timestamp}] {seg.text}"
        for seg in transcription
    ])

    # Create the prompt for Gemini
    prompt = f"""Analyze the following video transcript and identify the {max_clips} MOST ENGAGING moments that would make great short-form clips (TikTok, Instagram Reels, YouTube Shorts).

TRANSCRIPT:
{transcript_text}

TARGET CLIP LENGTH: {desired_length} seconds (can vary ±15 seconds for natural breaks)

SELECTION CRITERIA:
1. **Hook/Attention Grabber**: Moments that immediately capture attention
2. **Valuable Content**: Actionable tips, insights, or key takeaways
3. **Emotional Impact**: Funny, surprising, inspiring, or relatable moments
4. **Standalone Value**: Can be understood without full context
5. **Visual Interest**: Mentions screen shares, demos, or visual examples
6. **Cliffhangers/Curiosity**: Moments that make viewers want more

For each clip suggestion, provide:
- Start timestamp (in seconds)
- End timestamp (in seconds)
- Duration (in seconds)
- Reason why this moment is engaging
- The key hook/phrase that grabs attention
- Engagement score (0-10)
- Brief preview of what's being said

Return ONLY a JSON array with this exact structure:
[
  {{
    "start_time": 45.0,
    "end_time": 98.0,
    "duration": 53.0,
    "reason": "Strong hook about productivity followed by actionable tip",
    "hook_text": "This one trick changed everything",
    "engagement_score": 8.5,
    "transcript_preview": "This one trick changed everything for my workflow..."
  }}
]

IMPORTANT:
- Return ONLY valid JSON, no markdown, no explanation
- Ensure clips don't overlap
- Prioritize quality over quantity - fewer great clips is better than many mediocre ones
- Consider natural speech breaks for start/end times
- Engagement score should reflect viral potential (7+ is excellent)
"""

    try:
        # Use Gemini Flash for fast analysis
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)

        # Extract JSON from response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL).group(1)
        elif "```" in response_text:
            response_text = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL).group(1)

        # Parse JSON response
        clips_data = json.loads(response_text)

        # Convert to ClipSuggestion objects
        clip_suggestions = []
        for clip in clips_data:
            # Validate that start_time exists in transcription
            if clip["start_time"] < 0 or clip["end_time"] > transcription[-1].end_seconds:
                continue

            clip_suggestions.append(ClipSuggestion(
                start_time=clip["start_time"],
                end_time=clip["end_time"],
                duration=clip["duration"],
                reason=clip["reason"],
                hook_text=clip["hook_text"],
                engagement_score=clip["engagement_score"],
                transcript_preview=clip.get("transcript_preview", "")
            ))

        # Sort by engagement score (highest first)
        clip_suggestions.sort(key=lambda x: x.engagement_score, reverse=True)

        return clip_suggestions[:max_clips]

    except Exception as e:
        print(f"Error analyzing transcript for clips: {str(e)}")
        # Return empty list on error
        return []


def validate_clip_timing(clip: ClipSuggestion, video_duration: float) -> bool:
    """
    Validate that clip timing is valid

    Args:
        clip: ClipSuggestion to validate
        video_duration: Total video duration in seconds

    Returns:
        True if clip timing is valid, False otherwise
    """
    if clip.start_time < 0:
        return False
    if clip.end_time > video_duration:
        return False
    if clip.start_time >= clip.end_time:
        return False
    if clip.duration <= 0:
        return False
    if abs((clip.end_time - clip.start_time) - clip.duration) > 1.0:
        # Allow 1 second tolerance for rounding
        return False

    return True


def get_transcript_for_clip(
    transcription: List[TranscriptionSegment],
    start_time: float,
    end_time: float
) -> str:
    """
    Extract transcript text for a specific time range

    Args:
        transcription: Full transcription segments
        start_time: Clip start time in seconds
        end_time: Clip end time in seconds

    Returns:
        Concatenated transcript text for the clip
    """
    clip_text = []

    for segment in transcription:
        # Check if segment overlaps with clip time range
        if segment.start_seconds >= start_time and segment.start_seconds < end_time:
            clip_text.append(segment.text)
        elif segment.end_seconds and segment.end_seconds > start_time and segment.start_seconds < end_time:
            clip_text.append(segment.text)

    return " ".join(clip_text)
