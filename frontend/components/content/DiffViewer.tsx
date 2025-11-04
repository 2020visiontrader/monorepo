'use client';

interface DiffViewerProps {
  original: string;
  modified: string;
  fieldName: string;
}

export default function DiffViewer({ original, modified, fieldName }: DiffViewerProps) {
  // Simple diff highlighting - in production, use a proper diff library
  const isDifferent = original !== modified;

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="border border-neutral-200 rounded-base">
        <div className="p-3 bg-neutral-50 border-b border-neutral-200">
          <p className="text-sm font-medium text-neutral-700">Original {fieldName}</p>
        </div>
        <div className="p-4">
          <pre className="text-sm text-neutral-700 whitespace-pre-wrap font-mono">{original}</pre>
        </div>
      </div>
      <div className="border border-neutral-200 rounded-base">
        <div className="p-3 bg-neutral-50 border-b border-neutral-200">
          <p className="text-sm font-medium text-neutral-700">New {fieldName}</p>
        </div>
        <div className="p-4">
          <pre
            className={`text-sm whitespace-pre-wrap font-mono ${
              isDifferent ? 'text-primary-700 bg-primary-50' : 'text-neutral-700'
            }`}
          >
            {modified}
          </pre>
        </div>
      </div>
    </div>
  );
}

