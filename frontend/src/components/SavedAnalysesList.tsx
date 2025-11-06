import React, { useEffect, useState } from 'react';
import { videoApi } from '../services/api';
import { SavedAnalysis } from '../types';
import { FileText, Clock, HardDrive, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

interface SavedAnalysesListProps {
  onLoadAnalysis: (filename: string) => void;
  isLoading?: boolean;
}

export const SavedAnalysesList: React.FC<SavedAnalysesListProps> = ({ onLoadAnalysis, isLoading }) => {
  const [analyses, setAnalyses] = useState<SavedAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await videoApi.listAnalyses();
      setAnalyses(response.analyses);
    } catch (err) {
      setError('Failed to load saved analyses');
      console.error('Error loading analyses:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    const kb = bytes / 1024;
    return `${kb.toFixed(1)} KB`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          <span className="ml-2 text-gray-600">Loading saved analyses...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-red-600 flex items-center">
          <span className="font-semibold">Error:</span>
          <span className="ml-2">{error}</span>
        </div>
      </div>
    );
  }

  if (analyses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center">No saved analyses found</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center">
          <FileText className="w-5 h-5 text-blue-500 mr-2" />
          <h2 className="text-lg font-semibold text-gray-800">
            Saved Analyses ({analyses.length})
          </h2>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-500" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-500" />
        )}
      </button>

      {/* List */}
      {isExpanded && (
        <div className="border-t border-gray-200">
          <div className="max-h-96 overflow-y-auto">
            {analyses.map((analysis) => (
              <div
                key={analysis.filename}
                className="border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors"
              >
                <button
                  onClick={() => onLoadAnalysis(analysis.filename)}
                  disabled={isLoading}
                  className="w-full p-4 text-left disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {analysis.original_filename}
                      </h3>
                      <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-500">
                        <div className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatDate(analysis.processed_at)}
                        </div>
                        <div className="flex items-center">
                          <span className="mr-1">⏱️</span>
                          {formatDuration(analysis.duration_seconds)}
                        </div>
                        <div className="flex items-center">
                          <HardDrive className="w-3 h-3 mr-1" />
                          {formatFileSize(analysis.file_size_bytes)}
                        </div>
                      </div>
                    </div>
                    {isLoading && (
                      <Loader2 className="w-4 h-4 animate-spin text-blue-500 ml-2" />
                    )}
                  </div>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
