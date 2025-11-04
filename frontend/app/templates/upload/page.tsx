'use client';

import { useState } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import Link from 'next/link';
import FileDropzone from '@/components/upload/FileDropzone';

export default function UploadTemplatePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    // Validate file
    const errors: string[] = [];
    if (file.name.endsWith('.json')) {
      // Would validate JSON schema here
      // For now, just check if it's valid JSON
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const json = JSON.parse(e.target?.result as string);
          if (!json.meta || !json.theme_tokens || !json.sections) {
            errors.push('Missing required fields: meta, theme_tokens, or sections');
            setValidationErrors(errors);
          } else {
            setValidationErrors([]);
          }
        } catch (err) {
          setValidationErrors(['Invalid JSON format']);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleError = (error: string) => {
    setValidationErrors([error]);
  };

  return (
    <LayoutShell
      pageTitle="Upload Template"
      pageSubtitle="Upload a custom store template (ZIP or JSON)"
    >
      <div className="max-w-2xl mx-auto">
        <div className="bg-white p-8 rounded-lg border border-neutral-200">
          <FileDropzone
            accept=".zip,.json"
            onFileSelect={handleFileSelect}
            onError={handleError}
            validationErrors={validationErrors}
          />

          <div className="mt-6">
            <h3 className="font-semibold mb-2">Template Requirements</h3>
            <ul className="text-sm text-neutral-600 space-y-1">
              <li>• Valid JSON schema or ZIP archive</li>
              <li>• Include theme_tokens, sections, and compatibility data</li>
              <li>• Preview images recommended</li>
            </ul>
          </div>

          <div className="flex gap-4 mt-8">
            <Link href="/templates" className="btn-secondary">
              Cancel
            </Link>
            <button
              className="btn-primary"
              disabled={!selectedFile || validationErrors.length > 0}
            >
              Upload Template
            </button>
          </div>
        </div>
      </div>
    </LayoutShell>
  );
}

