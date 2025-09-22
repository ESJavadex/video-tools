import React, { useState, useEffect } from 'react';
import { Youtube, AlertCircle, CheckCircle } from 'lucide-react';
import VideoUploader from './components/VideoUploader';
import TranscriptionViewer from './components/TranscriptionViewer';
import SuggestionsPanel from './components/SuggestionsPanel';
import ActionItemsPanel from './components/ActionItemsPanel';
import { videoApi } from './services/api';
import { VideoTranscriptionResponse } from './types';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<VideoTranscriptionResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    const isOnline = await videoApi.checkHealth();
    setApiStatus(isOnline ? 'online' : 'offline');
  };

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    setError('');
    setResult(null);

    try {
      const response = await videoApi.uploadAndProcess(file);
      setResult(response);
    } catch (err: any) {
      console.error('Error processing video:', err);
      setError(
        err.response?.data?.detail ||
        'Error al procesar el video. Por favor, intenta de nuevo.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const resetApp = () => {
    setResult(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-10">
          <div className="flex items-center justify-center mb-4">
            <Youtube className="w-12 h-12 text-red-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-800">
              YouTube Video Tools
            </h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Transcribe y optimiza tus videos con IA. Obtén transcripciones precisas,
            títulos atractivos, descripciones SEO y más.
          </p>

          {/* API Status */}
          <div className="mt-4 inline-flex items-center">
            {apiStatus === 'checking' && (
              <span className="text-sm text-gray-500">Verificando API...</span>
            )}
            {apiStatus === 'online' && (
              <span className="text-sm text-green-600 flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                API conectada
              </span>
            )}
            {apiStatus === 'offline' && (
              <span className="text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                API desconectada - Inicia el servidor backend
              </span>
            )}
          </div>
        </header>

        {/* Main Content */}
        {!result ? (
          <div className="max-w-4xl mx-auto">
            <VideoUploader
              onFileSelect={handleFileSelect}
              isProcessing={isProcessing}
            />

            {error && (
              <div className="max-w-2xl mx-auto mt-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
                  <div>
                    <p className="text-red-700">{error}</p>
                    {apiStatus === 'offline' && (
                      <p className="text-sm text-red-600 mt-2">
                        Asegúrate de que el servidor backend esté ejecutándose:
                        <code className="bg-red-100 px-2 py-1 rounded ml-2">
                          cd backend && python -m uvicorn app.main:app --reload
                        </code>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="max-w-7xl mx-auto">
            <div className="mb-6 text-center">
              <button
                onClick={resetApp}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Procesar otro video
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-6">
                <TranscriptionViewer transcription={result.transcription} />
              </div>
              <div className="space-y-6">
                <SuggestionsPanel
                  suggestions={result.suggestions}
                  transcription={result.transcription}
                />

                {/* Action Items */}
                {result.suggestions?.action_items && result.suggestions.action_items.length > 0 && (
                  <ActionItemsPanel actionItems={result.suggestions.action_items} />
                )}

                {/* Metadata */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">
                    Información del video
                  </h3>
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Archivo original:</dt>
                      <dd className="text-gray-700">{result.original_filename}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Duración:</dt>
                      <dd className="text-gray-700">
                        {Math.floor(result.duration_seconds / 60)}:
                        {String(Math.floor(result.duration_seconds % 60)).padStart(2, '0')}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Procesado:</dt>
                      <dd className="text-gray-700">
                        {new Date(result.processed_at).toLocaleString('es-ES')}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        {!result && !isProcessing && (
          <div className="max-w-4xl mx-auto mt-12">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                ¿Cómo funciona?
              </h2>
              <ol className="space-y-3 text-gray-600">
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0">
                    1
                  </span>
                  <span>Sube tu video (formatos soportados: MP4, AVI, MOV, MKV, WebM, MPEG)</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0">
                    2
                  </span>
                  <span>La IA transcribirá automáticamente el audio con timestamps precisos</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0">
                    3
                  </span>
                  <span>Recibe sugerencias optimizadas: título, descripción, thumbnail y capítulos</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0">
                    4
                  </span>
                  <span>Copia y usa las sugerencias directamente en YouTube</span>
                </li>
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;