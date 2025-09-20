import React, { useState, useRef } from 'react';
import { Upload, Film, AlertCircle } from 'lucide-react';

interface VideoUploaderProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

const VideoUploader: React.FC<VideoUploaderProps> = ({ onFileSelect, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const inputRef = useRef<HTMLInputElement>(null);

  const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mpeg'];
  const maxFileSize = 5 * 1024 * 1024 * 1024; // 5GB

  const validateFile = (file: File): boolean => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setError(`Formato no permitido. Formatos aceptados: ${allowedExtensions.join(', ')}`);
      return false;
    }

    if (file.size > maxFileSize) {
      setError(`El archivo es muy grande. Máximo: ${maxFileSize / (1024 * 1024 * 1024)}GB`);
      return false;
    }

    setError('');
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={!isProcessing ? handleClick : undefined}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={allowedExtensions.join(',')}
          onChange={handleChange}
          disabled={isProcessing}
        />

        <div className="flex flex-col items-center">
          {selectedFile ? (
            <Film className="w-16 h-16 text-blue-500 mb-4" />
          ) : (
            <Upload className="w-16 h-16 text-gray-400 mb-4" />
          )}

          {selectedFile ? (
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-700">
                {selectedFile.name}
              </p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              {!isProcessing && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    setError('');
                  }}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Cambiar archivo
                </button>
              )}
            </div>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Arrastra tu video aquí
              </p>
              <p className="text-sm text-gray-500">
                o haz clic para seleccionar
              </p>
              <p className="text-xs text-gray-400 mt-2">
                Formatos: {allowedExtensions.join(', ')} • Máx: 5GB
              </p>
            </>
          )}

          {isProcessing && (
            <div className="mt-4">
              <div className="inline-flex items-center">
                <svg
                  className="animate-spin h-5 w-5 text-blue-500 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span className="text-blue-600">Procesando video...</span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Esto puede tardar unos minutos
              </p>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
};

export default VideoUploader;