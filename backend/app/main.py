from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import videos
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="YouTube Video Tools API",
    description="API for processing YouTube videos with AI-powered transcription and suggestions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos.router)

@app.get("/")
async def root():
    return {
        "message": "YouTube Video Tools API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/videos/upload",
            "transcribe": "/api/videos/transcribe/{video_id}",
            "process": "/api/videos/process",
            "health": "/api/videos/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "api-gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)