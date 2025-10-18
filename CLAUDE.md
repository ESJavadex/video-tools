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

Full-stack YouTube video processing application using **OpenAI Whisper** for local transcription and **Google Gemini AI** for content analysis and suggestions.

### Backend Architecture (FastAPI + Python)
- **FastAPI** server with async/await patterns and multipart file upload support
- **Dual AI integration**:
  - **Local Whisper** (`whisper_service.py`) - Primary transcription engine (model: "small")
  - **Gemini AI** (`gemini.py`) - Fallback transcription + content suggestions (model: "gemini-2.0-flash-exp")
- **Pydantic models** for type safety and API contracts
- **Service-oriented architecture**:
  - `app/main.py` - FastAPI app configuration, CORS, and router registration
  - `app/config.py` - Settings management with pydantic-settings (environment variables)
  - `app/services/whisper_service.py` - Local video transcription with OpenAI Whisper
  - `app/services/suggestions_service.py` - Gemini-based content suggestions and regeneration
  - `app/services/video_processor.py` - Orchestration layer coordinating Whisper + Gemini
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
4. **AI Analysis**: Gemini processes transcription text and generates:
   - Optimized YouTube title (max 60 chars)
   - SEO description (150-200 words)
   - Thumbnail prompt (detailed visual description)
   - 15-30 video highlights/chapters with timestamps
   - Action items with priority levels (alta/media/baja)
5. **Response Parsing**: Backend structures Gemini's JSON response into Pydantic models
6. **Auto-Save**: Analysis results saved to `backend/analysis_results/` with timestamp
7. **Frontend Display**: Results shown with copy-to-clipboard functionality

### Regeneration Flow
- User can regenerate suggestions with custom instructions
- Transcription remains static (cached from initial processing)
- Gemini generates 4 alternative titles + updated suggestions
- Uses unique analysis ID to bypass Gemini caching

### Environment Configuration
- **Backend**: Requires `GEMINI_API_KEY` in `backend/.env` file
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
- **Gemini Model**: "gemini-2.0-flash-exp" for fast, cost-effective suggestions
- **Cache Busting**: Analysis ID with timestamp ensures no stale Gemini cache hits
- **Fallback**: Whisper → Gemini transcription chain ensures reliability

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