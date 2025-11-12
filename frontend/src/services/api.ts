import axios from 'axios';
import { VideoTranscriptionResponse, ClipGenerationResponse, AnalysesListResponse } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1800000, // 30 minutes for large video processing (3GB+ files can take 15-30 min with Whisper)
});

export const videoApi = {
  async uploadAndProcess(file: File): Promise<VideoTranscriptionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<VideoTranscriptionResponse>(
      '/videos/process',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
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

    const response = await api.post<ClipGenerationResponse>(
      '/videos/generate-clips',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
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