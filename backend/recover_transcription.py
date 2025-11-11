#!/usr/bin/env python3
"""
Transcription Recovery Utility

This script helps recover transcriptions from progress files when processing fails.
It can list all in-progress or failed transcription jobs and recover completed transcriptions.

Usage:
    python recover_transcription.py list              # List all transcription jobs
    python recover_transcription.py recover <file>    # Recover specific transcription
    python recover_transcription.py latest            # Recover most recent transcription
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROGRESS_DIR = "analysis_results/transcription_progress"
ANALYSIS_DIR = "analysis_results"
BACKUP_DIR = "analysis_results/transcription_backups"

def list_transcription_jobs():
    """List all transcription jobs with their status"""
    if not os.path.exists(PROGRESS_DIR):
        print(f"No progress directory found at {PROGRESS_DIR}")
        return

    files = sorted(
        [f for f in os.listdir(PROGRESS_DIR) if f.endswith("_progress.json")],
        reverse=True  # Most recent first
    )

    if not files:
        print("No transcription jobs found.")
        return

    print("\n" + "="*80)
    print("TRANSCRIPTION JOBS")
    print("="*80 + "\n")

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(PROGRESS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            status = data.get("status", "unknown")
            original_file = data.get("original_filename", "Unknown")
            started = data.get("started_at", "Unknown")
            stage = data.get("stage", "unknown")
            progress = data.get("progress_percent", 0)

            # Color code by status
            status_symbol = {
                "complete": "✓",
                "failed": "✗",
                "in_progress": "⟳",
                "started": "▶"
            }.get(status, "?")

            print(f"{i}. {status_symbol} {filename}")
            print(f"   Original: {original_file}")
            print(f"   Status: {status} ({stage} - {progress}%)")
            print(f"   Started: {started}")

            # Check if transcription was saved
            has_raw = data.get("raw_whisper_result") is not None
            has_formatted = data.get("formatted_segments") is not None

            if has_raw or has_formatted:
                segments = len(data.get("formatted_segments", [])) or len(data.get("raw_whisper_result", {}).get("segments", []))
                print(f"   💾 TRANSCRIPTION SAVED: {segments} segments available!")

            if data.get("error"):
                print(f"   Error: {data['error'][:100]}...")

            print()

        except Exception as e:
            print(f"{i}. ⚠ {filename} - Error reading: {e}\n")

def recover_transcription(filename: str):
    """Recover a transcription from a progress file"""
    filepath = os.path.join(PROGRESS_DIR, filename)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if we have transcription data
        formatted_segments = data.get("formatted_segments")
        raw_whisper = data.get("raw_whisper_result")

        if not formatted_segments and not raw_whisper:
            print("Error: No transcription data found in this file.")
            return False

        # Use formatted segments if available, otherwise convert raw
        if formatted_segments:
            segments = formatted_segments
            duration = data.get("duration", 0)
            print(f"✓ Found {len(segments)} formatted segments")
        else:
            # Convert raw Whisper segments to our format
            raw_segments = raw_whisper.get("segments", [])
            segments = []
            for seg in raw_segments:
                start_time = seg.get('start', 0)
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"

                segments.append({
                    "timestamp": timestamp,
                    "text": seg.get("text", "").strip(),
                    "start_seconds": start_time,
                    "end_seconds": seg.get("end", start_time + 1)
                })
            duration = raw_whisper.get("duration", 0)
            print(f"✓ Converted {len(segments)} raw Whisper segments")

        # Save to analysis results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = data.get("original_filename", "recovered_video")
        clean_filename = "".join(c for c in original_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_filename = clean_filename.replace(' ', '_')

        os.makedirs(ANALYSIS_DIR, exist_ok=True)
        output_filename = f"{timestamp}_{clean_filename}_RECOVERED_analysis.json"
        output_path = os.path.join(ANALYSIS_DIR, output_filename)

        recovery_data = {
            "original_filename": original_filename,
            "analysis_id": data.get("video_id", "recovered"),
            "processed_at": data.get("completed_at") or data.get("whisper_completed_at") or datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "recovered": True,
            "recovery_source": filename,
            "transcription": segments,
            "suggestions": {
                "title": f"RECOVERED: {original_filename}",
                "description": "This transcription was recovered from a failed processing job. Use the regenerate feature to generate AI suggestions.",
                "thumbnail_prompt": "Video thumbnail",
                "highlights": [],
                "action_items": []
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(recovery_data, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*80}")
        print(f"✓ TRANSCRIPTION RECOVERED SUCCESSFULLY!")
        print(f"{'='*80}")
        print(f"Segments recovered: {len(segments)}")
        print(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        print(f"Saved to: {output_path}")
        print(f"\nYou can now:")
        print(f"1. Load this analysis in the frontend using the 'Load Saved Analysis' feature")
        print(f"2. Use the 'Regenerate Suggestions' button to get AI-generated suggestions")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"Error recovering transcription: {e}")
        import traceback
        traceback.print_exc()
        return False

def recover_latest():
    """Recover the most recent transcription"""
    if not os.path.exists(PROGRESS_DIR):
        print(f"No progress directory found at {PROGRESS_DIR}")
        return

    files = sorted(
        [f for f in os.listdir(PROGRESS_DIR) if f.endswith("_progress.json")],
        reverse=True  # Most recent first
    )

    if not files:
        print("No transcription jobs found.")
        return

    print(f"Attempting to recover latest transcription: {files[0]}\n")
    recover_transcription(files[0])

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "list":
        list_transcription_jobs()
    elif command == "recover" and len(sys.argv) >= 3:
        filename = sys.argv[2]
        recover_transcription(filename)
    elif command == "latest":
        recover_latest()
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
