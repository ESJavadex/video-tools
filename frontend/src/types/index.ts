export interface TranscriptionSegment {
  timestamp: string;
  text: string;
  start_seconds: number;
  end_seconds?: number;
}

export interface ActionItem {
  action: string;
  context: string;
  priority: string;
}

export interface VideoSuggestions {
  title: string;
  titles?: string[]; // Multiple title options
  description: string;
  thumbnail_prompt: string;
  thumbnail_texts?: string[]; // Clickbait texts for thumbnail overlay
  highlights: TranscriptionSegment[];
  action_items?: ActionItem[];
  linkedin_post?: string; // LinkedIn post for sharing
}

export interface VideoTranscriptionResponse {
  id: string;
  original_filename: string;
  transcription: TranscriptionSegment[];
  suggestions: VideoSuggestions;
  duration_seconds: number;
  processed_at: string;
}

export interface VideoUploadResponse {
  id: string;
  filename: string;
  file_path: string;
  size_mb: number;
  uploaded_at: string;
}

export interface RegenerateSuggestionsRequest {
  transcription: TranscriptionSegment[];
  custom_instructions?: string;
}

export interface RegenerateSuggestionsResponse {
  titles: string[];
  description: string;
  thumbnail_prompt: string;
  thumbnail_texts?: string[]; // Clickbait texts for thumbnail overlay
  linkedin_post?: string; // LinkedIn post for sharing
}

export interface ClipSuggestion {
  start_time: number;
  end_time: number;
  duration: number;
  reason: string;
  hook_text: string;
  engagement_score: number;
  transcript_preview: string;
}

export interface PersonDetectionInfo {
  face_detected: boolean;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}

export interface ProcessedClip {
  clip_id: string;
  suggestion: ClipSuggestion;
  file_path: string;
  file_size_mb: number;
  resolution: string;
  person_detection?: PersonDetectionInfo;
}

export interface ClipGenerationResponse {
  clips: ProcessedClip[];
  total_clips: number;
  processing_time_seconds: number;
  generated_at: string;
}

export interface SavedAnalysis {
  filename: string;
  original_filename: string;
  analysis_id: string;
  processed_at: string;
  duration_seconds: number;
  file_size_bytes: number;
}

export interface AnalysesListResponse {
  analyses: SavedAnalysis[];
}