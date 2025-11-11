# Transcription Safety System

## 🛡️ Overview

This system ensures that **transcriptions are never lost**, even if the process crashes or fails during AI suggestions generation.

## 🔄 How It Works

### Multi-Layer Protection

1. **Progress Tracking** (Real-time)
   - Creates a progress file immediately when transcription starts
   - Updates progress at each stage: `initializing` → `extracting_audio` → `transcribing` → `transcription_complete` → `complete`
   - Saves transcription data **immediately** after Whisper completes, before calling Gemini

2. **Immediate Backup** (After Whisper)
   - Saves raw Whisper result with all segments
   - Saves formatted transcription segments
   - Both saves happen **before** the risky Gemini API call

3. **Graceful Degradation** (Gemini Failure)
   - If Gemini fails, the system returns the transcription with default suggestions
   - User can regenerate suggestions later without re-transcribing

## 📁 File Structure

```
backend/
├── analysis_results/
│   ├── transcription_progress/          # Real-time progress tracking
│   │   └── 20251111_230045_abc123_progress.json
│   ├── transcription_backups/           # Post-Whisper backups
│   │   └── 20251111_230145_video_transcription.json
│   └── 20251111_230245_video_analysis.json  # Final result
└── recover_transcription.py             # Recovery utility
```

## 🔍 Progress File Format

```json
{
  "video_id": "unique-id",
  "video_path": "uploads/video.mp4",
  "original_filename": "My Video.mp4",
  "started_at": "2025-11-11T23:00:00Z",
  "status": "in_progress",
  "stage": "transcribing",
  "progress_percent": 50,

  // ✓ Saved immediately after Whisper completes
  "raw_whisper_result": {
    "segments": [...],  // Full Whisper segments
    "language": "spanish",
    "duration": 3720.5,
    "text": "Complete transcription..."
  },
  "whisper_completed_at": "2025-11-11T23:15:00Z",

  // ✓ Saved after formatting
  "formatted_segments": [
    {
      "timestamp": "00:00",
      "text": "Bienvenido...",
      "start_seconds": 0.0,
      "end_seconds": 5.2
    }
  ],
  "segment_count": 582,
  "duration": 3720.5,

  // Error tracking
  "error": null  // or error message if failed
}
```

## 🚀 Recovery Utility

### Commands

```bash
# List all transcription jobs
python recover_transcription.py list

# Recover specific job
python recover_transcription.py recover 20251111_230045_abc123_progress.json

# Recover most recent job
python recover_transcription.py latest
```

### Recovery Process

1. Script reads the progress file
2. Extracts transcription (formatted or raw)
3. Converts to standard analysis format
4. Saves to `analysis_results/` with `_RECOVERED_` prefix
5. File can be loaded in frontend and regenerated

### Example Recovery

```bash
$ python recover_transcription.py list

================================================================================
TRANSCRIPTION JOBS
================================================================================

1. ✓ 20251111_230045_abc123_progress.json
   Original: podcast_episode.mov
   Status: failed (transcription_complete - 90%)
   Started: 2025-11-11T23:00:45Z
   💾 TRANSCRIPTION SAVED: 582 segments available!

$ python recover_transcription.py recover 20251111_230045_abc123_progress.json

================================================================================
✓ TRANSCRIPTION RECOVERED SUCCESSFULLY!
================================================================================
Segments recovered: 582
Duration: 3720.50 seconds (62.0 minutes)
Saved to: analysis_results/20251111_231500_podcast_episode_RECOVERED_analysis.json

You can now:
1. Load this analysis in the frontend using the 'Load Saved Analysis' feature
2. Use the 'Regenerate Suggestions' button to get AI-generated suggestions
================================================================================
```

## 🎯 Usage Scenarios

### Scenario 1: Gemini API Fails
**What happens:**
- Whisper completes transcription (582 segments)
- Gemini API fails with quota/timeout error
- System returns transcription with default suggestions
- User sees message: "AI suggestions failed. Use regenerate feature."

**Recovery:**
- Transcription is already saved in final analysis file
- User clicks "Regenerate Suggestions" button
- Gemini generates suggestions without re-transcribing

### Scenario 2: Process Crashes Mid-Transcription
**What happens:**
- Whisper is transcribing (50% complete)
- Server crashes or network drops
- No final result returned to user

**Recovery:**
```bash
python recover_transcription.py list
# Shows job at "transcribing - 50%"
# No transcription saved yet
# Must re-upload video
```

### Scenario 3: Process Crashes After Whisper Completes
**What happens:**
- Whisper completes (582 segments saved)
- Starting Gemini call...
- Process crashes

**Recovery:**
```bash
python recover_transcription.py latest
# ✓ Recovers all 582 segments
# Saves to analysis_results/
# Can load in frontend and regenerate suggestions
```

## 🔧 Technical Details

### Whisper Service Changes

**New method signatures:**
```python
def transcribe_video(
    self,
    video_path: str,
    language: str = "es",
    video_id: Optional[str] = None,           # Enable progress tracking
    original_filename: Optional[str] = None    # For progress metadata
) -> Dict[str, Any]
```

**New internal methods:**
- `_create_progress_file()` - Initialize tracking
- `_update_progress()` - Update stage/percentage
- `_save_raw_whisper_result()` - Save immediately after Whisper
- `_save_formatted_segments()` - Save after formatting

### Video Processor Changes

**Before:**
```python
whisper_result = self.whisper_service.transcribe_video(file_path, language="es")
suggestions = self.suggestions_service.generate_suggestions(...)  # ❌ If this fails, ALL is lost
```

**After:**
```python
whisper_result = self.whisper_service.transcribe_video(
    file_path, language="es",
    video_id=video_id,              # ✓ Enables progress tracking
    original_filename=original_filename
)
# ✓ Transcription saved immediately in progress file

try:
    suggestions = self.suggestions_service.generate_suggestions(...)
except Exception as gemini_error:
    # ✓ Graceful fallback - transcription is safe!
    suggestions = default_suggestions
```

## 📊 Progress Tracking Lifecycle

```
1. START
   ├─ Create progress file
   │  status: "started", stage: "initializing", progress: 0%
   │
2. AUDIO EXTRACTION
   ├─ Update progress
   │  status: "in_progress", stage: "extracting_audio", progress: 5%
   │
3. WHISPER TRANSCRIPTION (longest step)
   ├─ Update progress
   │  status: "in_progress", stage: "transcribing", progress: 10%
   │
4. WHISPER COMPLETE ⚡ CRITICAL SAVE POINT
   ├─ Save raw_whisper_result
   ├─ Save formatted_segments
   │  status: "in_progress", stage: "transcription_complete", progress: 90%
   │  💾 ALL TRANSCRIPTION DATA IS NOW SAFE
   │
5. GEMINI SUGGESTIONS (can fail safely)
   ├─ Try to generate suggestions
   │  If fails → Use default suggestions
   │
6. COMPLETE
   └─ Final save
      status: "complete", stage: "complete", progress: 100%
```

## 🚨 Error Handling

### Whisper Fails
- Progress file shows: `status: "failed", error: "Whisper transcription failed: ..."`
- No transcription to recover
- User must re-upload video

### Gemini Fails (After Whisper Succeeds)
- Progress file has complete transcription saved
- System returns transcription with default suggestions
- User can regenerate suggestions anytime

### Server Crashes
- Progress files remain on disk
- Use recovery utility to extract saved transcription
- If Whisper hadn't completed, no transcription to recover

## ✅ Best Practices

1. **Monitor progress directory** - Check `transcription_progress/` for stuck jobs
2. **Run recovery regularly** - Use `python recover_transcription.py list` to find recoverable jobs
3. **Keep progress files** - Don't delete until final analysis is confirmed
4. **Use regenerate feature** - If suggestions are poor, regenerate without re-transcribing

## 🔮 Future Improvements

- [ ] Add webhook/notification when transcription completes
- [ ] Implement resumable transcription (save every N segments)
- [ ] Add progress percentage to frontend UI
- [ ] Auto-recovery: detect and recover failed jobs on server restart
- [ ] Progress API endpoint: GET /api/videos/progress/{video_id}
