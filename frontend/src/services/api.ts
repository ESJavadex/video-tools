import axios from 'axios';
import { VideoTranscriptionResponse, ClipGenerationResponse, AnalysesListResponse } from '../types';

// For large file uploads, bypass Vite proxy and go directly to backend
const DIRECT_BACKEND_URL = 'http://localhost:8009/api';
const API_BASE_URL = '/api';

// Large file threshold: 500MB - files larger than this bypass the Vite proxy
const LARGE_FILE_THRESHOLD = 500 * 1024 * 1024;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1800000, // 30 minutes for large video processing (3GB+ files can take 15-30 min with Whisper)
});

const directApi = axios.create({
  baseURL: DIRECT_BACKEND_URL,
  timeout: 1800000,
  maxContentLength: Infinity,
  maxBodyLength: Infinity,
});

export const videoApi = {
  async uploadAndProcess(file: File): Promise<VideoTranscriptionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    // Use direct backend connection for large files to bypass Vite proxy limitations
    const client = file.size > LARGE_FILE_THRESHOLD ? directApi : api;

    const response = await client.post<VideoTranscriptionResponse>(
      '/videos/process',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
      }
    );

    return response.data;
  },

  async checkHealth(): Promise<boolean> {
    try {
      await api.get('/videos/health');
      return true;
    } catch {
      return false;
    }
  },

  async generateClips(
    file: File,
    desiredLength: number = 60,
    maxClips: number = 5,
    formatType: string = 'tiktok'
  ): Promise<ClipGenerationResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('desired_length', desiredLength.toString());
    formData.append('max_clips', maxClips.toString());
    formData.append('format_type', formatType);

    // Use direct backend connection for large files to bypass Vite proxy limitations
    const client = file.size > LARGE_FILE_THRESHOLD ? directApi : api;

    const response = await client.post<ClipGenerationResponse>(
      '/videos/generate-clips',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
      }
    );

    return response.data;
  },

  async listAnalyses(): Promise<AnalysesListResponse> {
    const response = await api.get<AnalysesListResponse>('/videos/analyses');
    return response.data;
  },

  async loadAnalysis(filename: string): Promise<VideoTranscriptionResponse> {
    const response = await api.get<VideoTranscriptionResponse>(`/videos/analyses/${filename}`);
    return response.data;
  },
};