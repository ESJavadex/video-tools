import React, { useState } from 'react';
import { Clock, Copy, Check, Download } from 'lucide-react';
import { TranscriptionSegment } from '../types';

interface TranscriptionViewerProps {
  transcription: TranscriptionSegment[];
}

const TranscriptionViewer: React.FC<TranscriptionViewerProps> = ({ transcription }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [copiedAll, setCopiedAll] = useState(false);

  const copyToClipboard = (text: string, index?: number) => {
    navigator.clipboard.writeText(text);
    if (index !== undefined) {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } else {
      setCopiedAll(true);
      setTimeout(() => setCopiedAll(false), 2000);
    }
  };

  const downloadTranscription = () => {
    const content = transcription
      .map(seg => `[${seg.timestamp}] ${seg.text}`)
      .join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcripcion.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getAllText = () => {
    return transcription.map(seg => `[${seg.timestamp}] ${seg.text}`).join('\n');
  };

  if (!transcription || transcription.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No hay transcripción disponible
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-800">
            Transcripción
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => copyToClipboard(getAllText())}
              className="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors text-sm"
            >
              {copiedAll ? (
                <>
                  <Check className="w-4 h-4 mr-1" />
                  Copiado
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-1" />
                  Copiar todo
                </>
              )}
            </button>
            <button
              onClick={downloadTranscription}
              className="inline-flex items-center px-3 py-1.5 bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors text-sm"
            >
              <Download className="w-4 h-4 mr-1" />
              Descargar
            </button>
          </div>
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        <div className="p-6 space-y-3">
          {transcription.map((segment, index) => (
            <div
              key={index}
              className="group flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="flex items-center text-sm text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded">
                  <Clock className="w-3 h-3 mr-1" />
                  {segment.timestamp}
                </div>
              </div>
              <div className="flex-1">
                <p className="text-gray-700 leading-relaxed">
                  {segment.text}
                </p>
              </div>
              <button
                onClick={() => copyToClipboard(`[${segment.timestamp}] ${segment.text}`, index)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-200 rounded"
                title="Copiar segmento"
              >
                {copiedIndex === index ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4 text-gray-500" />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TranscriptionViewer;