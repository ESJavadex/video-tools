import axios from 'axios';
import { VideoTranscriptionResponse } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes for video processing
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
};