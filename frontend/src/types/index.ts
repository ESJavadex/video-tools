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
  highlights: TranscriptionSegment[];
  action_items?: ActionItem[];
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
}