'use client';

import { Upload, X, AlertCircle } from 'lucide-react';
import { useState, useRef } from 'react';

interface FileDropzoneProps {
  accept?: string;
  maxSize?: number; // in bytes
  onFileSelect: (file: File) => void;
  onError?: (error: string) => void;
  validationErrors?: string[];
}

export default function FileDropzone({
  accept = '.zip,.json',
  maxSize = 10 * 1024 * 1024, // 10MB default
  onFileSelect,
  onError,
  validationErrors = [],
}: FileDropzoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Validate file type
    const validExtensions = accept.split(',').map((ext) => ext.trim().replace('.', ''));
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    if (!fileExtension || !validExtensions.includes(fileExtension)) {
      const error = `Invalid file type. Accepted: ${accept}`;
      onError?.(error);
      return;
    }

    // Validate file size
    if (file.size > maxSize) {
      const error = `File too large. Maximum size: ${(maxSize / 1024 / 1024).toFixed(0)}MB`;
      onError?.(error);
      return;
    }

    setSelectedFile(file);
    onFileSelect(file);
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <div
        className={`border-2 border-dashed rounded-base p-12 text-center transition-colors ${
          dragActive
            ? 'border-primary-600 bg-primary-50'
            : 'border-neutral-300 hover:border-neutral-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <div className="flex items-center justify-center gap-3">
            <div className="flex-1 text-left">
              <p className="font-medium text-sm">{selectedFile.name}</p>
              <p className="text-xs text-neutral-600">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={removeFile}
              className="p-1 hover:bg-neutral-100 rounded-base transition-colors"
            >
              <X className="w-4 h-4 text-neutral-600" />
            </button>
          </div>
        ) : (
          <>
            <Upload className="w-12 h-12 mx-auto mb-4 text-neutral-400" />
            <p className="text-lg font-medium mb-2">Drop your template file here</p>
            <p className="text-sm text-neutral-600 mb-4">
              Supports {accept.replace(/\./g, '').toUpperCase()} files
            </p>
            <label className="btn-primary inline-block cursor-pointer">
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept={accept}
                onChange={handleFileInput}
              />
              Choose File
            </label>
          </>
        )}
      </div>

      {validationErrors.length > 0 && (
        <div className="mt-4 p-3 bg-accent-rose/10 border border-accent-rose/20 rounded-base">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-accent-rose flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-sm text-accent-rose mb-1">Validation Errors</p>
              <ul className="text-sm text-accent-rose space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

