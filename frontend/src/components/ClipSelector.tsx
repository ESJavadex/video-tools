import React, { useState } from 'react';
import {
  Scissors,
  Download,
  Play,
  Loader2,
  Sparkles,
  Clock,
  TrendingUp,
  Copy,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { ClipGenerationResponse, ProcessedClip } from '../types';
import { videoApi } from '../services/api';

interface ClipSelectorProps {
  videoFile?: File;
}

export const ClipSelector: React.FC<ClipSelectorProps> = ({ videoFile }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [clipResult, setClipResult] = useState<ClipGenerationResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [desiredLength, setDesiredLength] = useState(60);
  const [maxClips, setMaxClips] = useState(5);
  const [formatType, setFormatType] = useState<'tiktok' | 'instagram' | 'youtube-shorts'>('tiktok');
  const [copiedClipId, setCopiedClipId] = useState<string | null>(null);

  const handleGenerateClips = async () => {
    if (!videoFile) {
      setError('Please upload a video first');
      return;
    }

    setIsGenerating(true);
    setError('');
    setClipResult(null);

    try {
      const result = await videoApi.generateClips(videoFile, desiredLength, maxClips, formatType);
      setClipResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate clips. Please try again.');
      console.error('Error generating clips:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDownloadClip = (clip: ProcessedClip) => {
    // In a real implementation, this would download the clip file
    // For now, we'll show the file path
    alert(`Clip file path: ${clip.file_path}\n\nIn production, this would trigger a download.`);
  };

  const copyToClipboard = (text: string, clipId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedClipId(clipId);
    setTimeout(() => setCopiedClipId(null), 2000);
  };

  const getEngagementColor = (score: number): string => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Scissors className="w-6 h-6 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-900">AI Clip Generator</h2>
        <Sparkles className="w-5 h-5 text-purple-600" />
      </div>

      {/* Configuration Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Clip Length (seconds)
          </label>
          <input
            type="range"
            min="15"
            max="90"
            value={desiredLength}
            onChange={(e) => setDesiredLength(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            disabled={isGenerating}
          />
          <div className="text-center mt-1 text-sm font-semibold text-gray-900">
            {desiredLength}s
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Clips
          </label>
          <select
            value={maxClips}
            onChange={(e) => setMaxClips(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            disabled={isGenerating}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
              <option key={num} value={num}>{num} clip{num > 1 ? 's' : ''}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Format
          </label>
          <select
            value={formatType}
            onChange={(e) => setFormatType(e.target.value as any)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            disabled={isGenerating}
          >
            <option value="tiktok">TikTok (9:16)</option>
            <option value="instagram">Instagram Reels (9:16)</option>
            <option value="youtube-shorts">YouTube Shorts (9:16)</option>
          </select>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerateClips}
        disabled={isGenerating || !videoFile}
        className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating AI-Selected Clips...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Generate Clips with AI
          </>
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Processing Info */}
      {isGenerating && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 text-sm">
            This may take a few minutes. We're analyzing your video with AI to find the most engaging moments,
            detecting person location, and cropping to TikTok format...
          </p>
        </div>
      )}

      {/* Results Display */}
      {clipResult && (
        <div className="mt-6 space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <p className="text-green-800 font-medium">
                  {clipResult.total_clips} clips generated successfully!
                </p>
              </div>
              <span className="text-sm text-green-700">
                Processed in {clipResult.processing_time_seconds}s
              </span>
            </div>
          </div>

          {/* Clip Cards */}
          <div className="space-y-4">
            {clipResult.clips.map((clip, index) => (
              <div
                key={clip.clip_id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="bg-purple-600 text-white px-3 py-1 rounded-full text-sm font-bold">
                      #{index + 1}
                    </span>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">
                        {formatTime(clip.suggestion.start_time)} - {formatTime(clip.suggestion.end_time)}
                      </span>
                      <span className="text-sm text-gray-500 ml-2">
                        ({clip.suggestion.duration.toFixed(0)}s)
                      </span>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-semibold flex items-center gap-1 ${getEngagementColor(clip.suggestion.engagement_score)}`}>
                    <TrendingUp className="w-3 h-3" />
                    {clip.suggestion.engagement_score.toFixed(1)}/10
                  </div>
                </div>

                <div className="mb-3">
                  <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-yellow-500" />
                    {clip.suggestion.hook_text}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">{clip.suggestion.reason}</p>
                  <p className="text-xs text-gray-500 italic">
                    "{clip.suggestion.transcript_preview}"
                  </p>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{clip.resolution}</span>
                    <span>{clip.file_size_mb}MB</span>
                    {clip.person_detection?.face_detected && (
                      <span className="text-green-600 font-medium">
                        Person detected ({(clip.person_detection.confidence * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => copyToClipboard(clip.file_path, clip.clip_id)}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center gap-1"
                    >
                      {copiedClipId === clip.clip_id ? (
                        <>
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Path
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleDownloadClip(clip)}
                      className="px-3 py-1 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors flex items-center gap-1"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Box */}
      {!clipResult && !isGenerating && (
        <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            How it works
          </h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>AI analyzes your video transcript to find the most engaging moments</li>
            <li>Automatically detects person location for smart cropping</li>
            <li>Crops video to TikTok format (9:16) with 70% screen, 30% person</li>
            <li>Generates ready-to-post clips with viral potential scoring</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ClipSelector;
