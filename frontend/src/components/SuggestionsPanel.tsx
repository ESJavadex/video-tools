import React, { useState } from 'react';
import {
  FileText,
  Image,
  List,
  Copy,
  Check,
  Sparkles,
  Clock,
  RefreshCw,
  Settings
} from 'lucide-react';
import { VideoSuggestions, TranscriptionSegment, RegenerateSuggestionsResponse } from '../types';

interface SuggestionsPanelProps {
  suggestions: VideoSuggestions;
  transcription: TranscriptionSegment[];
}

const SuggestionsPanel: React.FC<SuggestionsPanelProps> = ({ suggestions, transcription }) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showCustomInstructions, setShowCustomInstructions] = useState(false);
  const [customInstructions, setCustomInstructions] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regeneratedSuggestions, setRegeneratedSuggestions] = useState<RegenerateSuggestionsResponse | null>(null);
  const [selectedTitleIndex, setSelectedTitleIndex] = useState<number>(0);

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const formatYouTubeChapters = () => {
    return suggestions.highlights
      .map(h => {
        // Convert timestamp to YouTube format (remove leading zeros)
        // "00:12" -> "0:12", "01:23" -> "1:23", "00:00:45" -> "0:00:45"
        const cleanTimestamp = h.timestamp.replace(/^0(\d):/, '$1:').replace(/^00:00:/, '0:00:');
        return `${cleanTimestamp} ${h.text}`;
      })
      .join('\n');
  };

  const handleRegenerateSuggestions = async () => {
    if (!transcription || transcription.length === 0) {
      alert('No hay transcripción disponible para regenerar sugerencias');
      return;
    }

    setIsRegenerating(true);
    try {
      const response = await fetch('/api/videos/regenerate-suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcription,
          custom_instructions: customInstructions.trim() || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));

        // Handle specific error types
        if (response.status === 429) {
          alert('⚠️ Límite de API alcanzado\n\nHas alcanzado el límite de cuota de Gemini API.\n\nSoluciones:\n1. Espera unos minutos y vuelve a intentarlo\n2. Verifica tu cuota en: https://aistudio.google.com/\n3. Considera actualizar tu plan de API\n\nError: ' + errorData.detail);
        } else if (response.status === 401) {
          alert('⚠️ Error de autenticación\n\nProblema con tu GEMINI_API_KEY.\n\nVerifica que:\n1. La clave esté configurada en backend/.env\n2. La clave sea válida\n3. Tengas permisos suficientes\n\nError: ' + errorData.detail);
        } else {
          alert('Error al regenerar sugerencias: ' + (errorData.detail || 'Error desconocido'));
        }
        return;
      }

      const data = await response.json();
      setRegeneratedSuggestions(data);
      setSelectedTitleIndex(0); // Reset to first title
      setShowCustomInstructions(false); // Close instructions panel
    } catch (error) {
      console.error('Error regenerating suggestions:', error);
      alert('Error de conexión al regenerar sugerencias. Verifica que el backend esté ejecutándose.');
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center">
            <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
            Sugerencias de Contenido
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowCustomInstructions(!showCustomInstructions)}
              className="text-sm text-gray-600 hover:text-gray-700 flex items-center border border-gray-300 rounded px-3 py-1"
            >
              <Settings className="w-4 h-4 mr-1" />
              Instrucciones
            </button>
            <button
              onClick={handleRegenerateSuggestions}
              disabled={isRegenerating}
              className="text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 flex items-center rounded px-3 py-1"
            >
              <RefreshCw className={`w-4 h-4 mr-1 ${isRegenerating ? 'animate-spin' : ''}`} />
              {isRegenerating ? 'Regenerando...' : 'Regenerar'}
            </button>
          </div>
        </div>

        {/* Custom Instructions Panel */}
        {showCustomInstructions && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instrucciones personalizadas (opcional)
            </label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="Ej: Enfócate en SEO, usa un tono más profesional, incluye palabras clave específicas..."
              className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
            <p className="text-xs text-gray-500 mt-2">
              Estas instrucciones se usarán para personalizar los títulos, descripción y thumbnail.
            </p>
          </div>
        )}
      </div>

      <div className="p-6 space-y-6">
        {/* Title Suggestions */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 flex items-center">
              <FileText className="w-4 h-4 mr-1" />
              {regeneratedSuggestions && regeneratedSuggestions.titles.length > 0
                ? `Títulos sugeridos (${regeneratedSuggestions.titles.length} opciones)`
                : 'Título sugerido'}
            </label>
            <button
              onClick={() => copyToClipboard(
                regeneratedSuggestions && regeneratedSuggestions.titles.length > 0
                  ? regeneratedSuggestions.titles[selectedTitleIndex]
                  : suggestions.title,
                'title'
              )}
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
            >
              {copiedField === 'title' ? (
                <>
                  <Check className="w-3 h-3 mr-1" />
                  Copiado
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 mr-1" />
                  Copiar
                </>
              )}
            </button>
          </div>

          {/* Multiple Title Options */}
          {regeneratedSuggestions && regeneratedSuggestions.titles.length > 0 ? (
            <div className="space-y-2">
              {regeneratedSuggestions.titles.map((title, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedTitleIndex(index)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedTitleIndex === index
                      ? 'bg-blue-100 border-2 border-blue-300'
                      : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500 font-medium">Opción {index + 1}</span>
                    {selectedTitleIndex === index && (
                      <Check className="w-4 h-4 text-blue-600" />
                    )}
                  </div>
                  <p className="text-gray-800 font-medium mt-1">{title}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-gray-800 font-medium">{suggestions.title}</p>
            </div>
          )}
        </div>

        {/* Description Suggestion */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 flex items-center">
              <FileText className="w-4 h-4 mr-1" />
              Descripción
            </label>
            <button
              onClick={() => copyToClipboard(
                regeneratedSuggestions?.description || suggestions.description,
                'description'
              )}
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
            >
              {copiedField === 'description' ? (
                <>
                  <Check className="w-3 h-3 mr-1" />
                  Copiado
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 mr-1" />
                  Copiar
                </>
              )}
            </button>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg max-h-32 overflow-y-auto">
            <p className="text-gray-700 whitespace-pre-wrap">
              {regeneratedSuggestions?.description || suggestions.description}
            </p>
          </div>
        </div>

        {/* Thumbnail Prompt */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 flex items-center">
              <Image className="w-4 h-4 mr-1" />
              Prompt para Thumbnail
            </label>
            <button
              onClick={() => copyToClipboard(
                regeneratedSuggestions?.thumbnail_prompt || suggestions.thumbnail_prompt,
                'thumbnail'
              )}
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
            >
              {copiedField === 'thumbnail' ? (
                <>
                  <Check className="w-3 h-3 mr-1" />
                  Copiado
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 mr-1" />
                  Copiar
                </>
              )}
            </button>
          </div>
          <div className="p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
            <p className="text-gray-700">
              {regeneratedSuggestions?.thumbnail_prompt || suggestions.thumbnail_prompt}
            </p>
          </div>
        </div>

        {/* YouTube Chapters - Formatted for direct paste */}
        {suggestions.highlights && suggestions.highlights.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 flex items-center">
                <List className="w-4 h-4 mr-1" />
                Capítulos de YouTube
              </label>
              <button
                onClick={() => copyToClipboard(formatYouTubeChapters(), 'youtube-chapters')}
                className="text-sm text-white bg-red-600 hover:bg-red-700 flex items-center px-3 py-1.5 rounded"
              >
                {copiedField === 'youtube-chapters' ? (
                  <>
                    <Check className="w-3 h-3 mr-1" />
                    Copiado
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3 mr-1" />
                    Copiar para YouTube
                  </>
                )}
              </button>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <pre className="text-sm text-gray-800 font-mono whitespace-pre-wrap">
                {formatYouTubeChapters()}
              </pre>
            </div>
            <p className="text-xs text-gray-500 italic">
              ✨ Formato listo para pegar en la descripción de YouTube. Los capítulos aparecerán automáticamente en el reproductor.
            </p>
          </div>
        )}

        {/* Highlights/Chapters - Visual Display */}
        {suggestions.highlights && suggestions.highlights.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                Vista previa de capítulos
              </label>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg space-y-2 max-h-48 overflow-y-auto">
              {suggestions.highlights.map((highlight, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <div className="flex items-center text-xs text-blue-600 font-mono bg-white px-2 py-1 rounded">
                    <Clock className="w-3 h-3 mr-1" />
                    {highlight.timestamp}
                  </div>
                  <p className="text-sm text-gray-700 flex-1">{highlight.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SuggestionsPanel;