# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI + Python)
```bash
cd backend
pip install -r requirements.txt              # Install dependencies
python -m uvicorn app.main:app --reload      # Start development server (port 8000)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000  # Production mode
```

### Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install                                  # Install dependencies
npm run dev                                  # Start development server (port 5173)
npm run build                               # Build for production
npm run lint                                # Run ESLint
npm run preview                             # Preview production build
```

## Architecture Overview

This is a full-stack YouTube video processing application with two main components:

### Backend Architecture
- **FastAPI** server with async/await patterns
- **Gemini AI integration** via `google-generativeai` SDK for video processing
- **Pydantic models** for type safety and API contracts
- **Router-based structure** with separation of concerns:
  - `app/main.py` - FastAPI app configuration and CORS
  - `app/config.py` - Settings management with pydantic-settings
  - `app/services/gemini.py` - Gemini AI API interactions
  - `app/services/video_processor.py` - Business logic layer
  - `app/routers/videos.py` - API endpoints
  - `app/models/video.py` - Pydantic models for API contracts

### Frontend Architecture
- **React + TypeScript** with functional components and hooks
- **Vite** as build tool with proxy to backend API
- **Tailwind CSS** for styling with custom components
- **Axios** for API communication with 10-minute timeout for video processing
- **Component structure**:
  - `App.tsx` - Main application state and layout
  - `VideoUploader.tsx` - Drag-and-drop file upload with validation
  - `TranscriptionViewer.tsx` - Display timestamped transcription
  - `SuggestionsPanel.tsx` - Show AI-generated content suggestions

### Data Flow
1. Frontend uploads video via multipart form data to `/api/videos/process`
2. Backend validates file (size: 5GB max, formats: MP4/AVI/MOV/MKV/WebM/MPEG)
3. Video uploaded to Gemini File API for processing
4. Gemini processes video and returns JSON with transcription + suggestions
5. Backend parses and structures response into typed models
6. Frontend displays results with copy-to-clipboard functionality

### Environment Configuration
- Backend requires `GEMINI_API_KEY` in `.env` file
- CORS configured for localhost:5173 and localhost:3000
- Vite proxy forwards `/api/*` requests to localhost:8000

### Key Integration Points
- **File Upload**: Handled via FastAPI's `UploadFile` with background cleanup
- **Gemini Processing**: Videos are uploaded to Gemini File API, then processed with custom prompt for Spanish transcription
- **Error Handling**: API errors propagated to frontend with user-friendly messages
- **State Management**: React state for upload progress, processing status, and results display

### Production Considerations
- Videos are temporarily stored in `uploads/` directory and cleaned up after processing
- File size validation enforced at both frontend (UX) and backend (security)
- API timeouts configured for long video processing operations
- Structured JSON responses from Gemini parsed with fallback text parsing