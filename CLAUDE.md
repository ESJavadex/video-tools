# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start (Both Backend & Frontend)
```bash
./run.sh                                     # Start both servers with auto-setup
```

### Backend (FastAPI + Python)
```bash
cd backend
python3 -m venv venv                         # Create virtual environment (first time)
source venv/bin/activate                     # Activate virtual environment
pip install -r requirements.txt              # Install dependencies
python -m uvicorn app.main:app --reload      # Start development server (port 8000)
python -m uvicorn app.main:app --reload --port 8000  # Explicit port specification
```

### Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install                                  # Install dependencies
npm run dev                                  # Start development server (port 5173)
npm run build                               # Build for production (compiles TypeScript first)
npm run lint                                # Run ESLint
npm run preview                             # Preview production build
```

## Architecture Overview

Full-stack YouTube video processing application using **OpenAI Whisper** for local transcription and **OpenAI GPT-4 / Google Gemini AI** (configurable) for content analysis and suggestions.

### Backend Architecture (FastAPI + Python)
- **FastAPI** server with async/await patterns and multipart file upload support
- **Multi-AI integration**:
  - **Local Whisper** (`whisper_service.py`) - Primary transcription engine (model: "small")
  - **OpenAI GPT-4** (`openai_service.py`) - AI suggestions with structured outputs (default, model: "gpt-4.1-mini")
  - **Gemini AI** (`gemini.py`) - Alternative AI provider + fallback transcription (model: "gemini-2.0-flash-exp")
- **Pydantic models** for type safety and API contracts
- **Service-oriented architecture**:
  - `app/main.py` - FastAPI app configuration, CORS, and router registration
  - `app/config.py` - Settings management with pydantic-settings (environment variables, AI provider selection)
  - `app/services/whisper_service.py` - Local video transcription with OpenAI Whisper
  - `app/services/openai_service.py` - OpenAI GPT-4 based content suggestions with structured outputs
  - `app/services/suggestions_service.py` - Gemini-based content suggestions and regeneration (alternative)
  - `app/services/video_processor.py` - Orchestration layer coordinating Whisper + AI provider
  - `app/routers/videos.py` - API endpoints for video processing and suggestion regeneration
  - `app/models/video.py` - Pydantic models (VideoTranscriptionResponse, VideoSuggestions, ActionItem, etc.)

### Frontend Architecture (React + TypeScript + Vite)
- **React 18** with functional components and hooks
- **TypeScript** for type safety across components
- **Vite** as build tool with development proxy (`/api/*` → `localhost:8000`)
- **Tailwind CSS** for styling
- **Axios** for API communication (10-minute timeout for long video processing)
- **Component structure**:
  - `App.tsx` - Main application state, layout, and result management
  - `VideoUploader.tsx` - Drag-and-drop file upload with client-side validation
  - `TranscriptionViewer.tsx` - Timestamped transcription display with copy functionality
  - `SuggestionsPanel.tsx` - AI-generated titles, descriptions, thumbnails, and highlights
  - `ActionItemsPanel.tsx` - Extracted action items with priority levels and copy features
- **Key dependencies**: lucide-react (icons), Playwright (for screenshot automation)

### Video Processing Flow
1. **Frontend Upload**: User uploads video via drag-and-drop to `/api/videos/process`
2. **Backend Validation**: FastAPI validates file size (max 5GB) and format (MP4/AVI/MOV/MKV/WebM/MPEG)
3. **Transcription (Two-Step Approach)**:
   - **Primary**: Local Whisper transcription (faster, no API costs, works offline)
   - **Fallback**: Gemini File API transcription (if Whisper fails)
4. **AI Analysis**: AI provider (OpenAI or Gemini) processes transcription text and generates:
   - Optimized YouTube title (max 60 chars)
   - SEO description (150-200 words)
   - Thumbnail prompt (detailed visual description)
   - 15-30 video highlights/chapters with timestamps
   - Action items with priority levels (alta/media/baja)
5. **Response Parsing**: Backend structures AI JSON response into Pydantic models (OpenAI uses native structured outputs)
6. **Auto-Save**: Analysis results saved to `backend/analysis_results/` with timestamp
7. **Frontend Display**: Results shown with copy-to-clipboard functionality

### Regeneration Flow
- User can regenerate suggestions with custom instructions
- Transcription remains static (cached from initial processing)
- AI provider generates 4 alternative titles + updated suggestions
- Uses unique analysis ID to bypass caching

### Environment Configuration
- **Backend AI Provider**: Configure in `backend/.env` file
  - `AI_PROVIDER` - Choose "openai" (default) or "gemini"
  - `OPENAI_API_KEY` - Required if using OpenAI (GPT-4)
  - `OPENAI_MODEL` - OpenAI model selection (default: "gpt-4.1-mini", also: "gpt-4.1-mini-mini", "gpt-4-turbo")
  - `GEMINI_API_KEY` - Required if using Gemini
- **CORS**: Configured for `localhost:5173` and `localhost:3000`
- **Vite Proxy**: Forwards `/api/*` requests to `localhost:8000` in development
- **File Storage**: Temporary uploads stored in `backend/uploads/` (auto-cleanup after processing)
- **Analysis Results**: JSON files saved to `backend/analysis_results/` with timestamps

### Key Technical Details

#### API Endpoints
- `POST /api/videos/process` - Upload and process video (returns transcription + suggestions)
- `POST /api/videos/regenerate-suggestions` - Regenerate suggestions with custom instructions
- `GET /api/videos/health` - Health check endpoint

#### File Handling
- **Upload**: FastAPI's `UploadFile` with temporary storage
- **Cleanup**: Background file deletion after processing completes
- **Validation**: Both frontend (UX) and backend (security) enforce 5GB max size

#### AI Processing Strategy
- **Whisper Model**: Uses "small" model for balance of speed/accuracy (supports videos 30+ min)
- **Language**: Default Spanish ("es"), configurable in service layer
- **OpenAI Models**:
  - "gpt-4.1-mini" (default) - Latest GPT-4 Omni for fast, high-quality suggestions with structured outputs
  - "gpt-4.1-mini-mini" - Cost-effective option for simpler content
  - "gpt-4-turbo" - High-capability model for complex analysis
- **Gemini Model**: "gemini-2.0-flash-exp" for fast, cost-effective suggestions (alternative provider)
- **Cache Busting**: Analysis ID with timestamp ensures no stale cache hits
- **Fallback Chain**: Whisper → Gemini transcription (if Whisper fails)
- **Provider Selection**: Choose AI provider in `.env` with `AI_PROVIDER` setting

#### Action Items Detection
- **Spanish Pattern Matching**: Detects future tense ("voy a", "haré"), promises ("tendrás"), commitments ("compartir")
- **Priority Classification**: alta (high) / media (medium) / baja (low)
- **ActionItem Model**: Fields include `action`, `context`, `priority`
- **Fallback**: Demo item included if no real actions detected (testing purposes)

#### Error Handling
- API errors propagated to frontend with user-friendly messages
- Whisper failures trigger automatic fallback to Gemini transcription
- File upload failures show clear error states in UI

#### State Management
- React state manages: upload progress, processing status, transcription, suggestions, action items
- No external state library (Redux/Zustand) - using built-in React hooks

## 🛡️ Transcription Safety System

### Overview
Multi-layer protection ensures transcriptions are **never lost**, even if processing crashes or Gemini API fails.

### Protection Layers

1. **Progress Tracking** (Real-time)
   - Creates progress file immediately when transcription starts: `analysis_results/transcription_progress/`
   - Updates at each stage: `initializing` → `extracting_audio` → `transcribing` → `transcription_complete` → `complete`
   - Saves transcription **immediately** after Whisper completes, before calling Gemini

2. **Immediate Backup** (Post-Whisper)
   - Saves raw Whisper result with all segments to progress file
   - Saves formatted transcription segments
   - Both saves happen **before** the risky Gemini API call

3. **Graceful Degradation** (Gemini Failure)
   - If Gemini fails, system returns transcription with default suggestions
   - User can regenerate suggestions later without re-transcribing
   - Error message: "AI suggestions failed. Use regenerate feature."

### Key Files

```
backend/
├── analysis_results/
│   ├── transcription_progress/          # Real-time progress tracking
│   ├── transcription_backups/           # Post-Whisper backups (legacy)
│   └── *_analysis.json                  # Final complete results
├── recover_transcription.py             # Recovery utility script
└── TRANSCRIPTION_SAFETY.md             # Full documentation
```

### Recovery Utility

```bash
# List all transcription jobs (shows status, progress, segments saved)
python recover_transcription.py list

# Recover specific job by filename
python recover_transcription.py recover 20251111_230045_abc123_progress.json

# Recover most recent job
python recover_transcription.py latest
```

### Technical Implementation

**Whisper Service** (`whisper_service.py`):
- New parameters: `video_id` and `original_filename` enable progress tracking
- Methods: `_create_progress_file()`, `_update_progress()`, `_save_raw_whisper_result()`, `_save_formatted_segments()`
- Progress saved to: `analysis_results/transcription_progress/{timestamp}_{video_id}_progress.json`

**Video Processor** (`video_processor.py`):
- Passes `video_id` and `original_filename` to Whisper service
- Wraps Gemini calls in try-catch with fallback to default suggestions
- Saves transcription backup before Gemini call (redundant safety)

**Progress File Format**:
```json
{
  "video_id": "abc123",
  "status": "in_progress",
  "stage": "transcription_complete",
  "progress_percent": 90,
  "raw_whisper_result": {
    "segments": [...],  // All Whisper segments
    "duration": 3720.5
  },
  "formatted_segments": [...],  // Ready-to-use format
  "error": null
}
```

### Recovery Scenarios

**Scenario 1: Gemini API Fails (Most Common)**
- Whisper completes successfully (e.g., 582 segments)
- Gemini times out or hits quota
- ✅ System returns transcription with default suggestions
- ✅ Transcription already in progress file + final analysis file
- User can click "Regenerate Suggestions" without re-uploading

**Scenario 2: Process Crashes After Whisper Completes**
- Whisper saves 582 segments to progress file
- Server crashes before Gemini runs
- ✅ Run: `python recover_transcription.py latest`
- ✅ Creates `*_RECOVERED_analysis.json` in `analysis_results/`
- Load in frontend, regenerate suggestions

**Scenario 3: Process Crashes During Whisper**
- Whisper still transcribing (50% complete)
- Server/network failure
- ❌ No transcription saved yet (Whisper doesn't support partial results)
- Must re-upload video

### Best Practices

1. **Monitor progress directory**: Check `analysis_results/transcription_progress/` for stuck jobs
2. **Run recovery utility**: Periodically run `list` command to find recoverable jobs
3. **Keep progress files**: Don't delete until final analysis confirmed successful
4. **Use regenerate feature**: If suggestions are poor, regenerate without re-transcribing

### Implementation Notes

- Whisper's `model.transcribe()` is atomic - returns all segments at once (no streaming)
- Progress file saves **immediately** after Whisper returns, before any Gemini calls
- ALTS/gRPC warnings from Gemini are harmless (occurs when running outside Google Cloud)
- Recovery script converts both raw and formatted segments to standard analysis format