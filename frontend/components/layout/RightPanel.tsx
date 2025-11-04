'use client';

import { X } from 'lucide-react';

interface RightPanelProps {
  children: React.ReactNode;
  onClose?: () => void;
}

export default function RightPanel({ children, onClose }: RightPanelProps) {
  return (
    <aside className="w-80 border-l border-neutral-200 bg-white p-6">
      {onClose && (
        <button
          onClick={onClose}
          className="mb-4 p-1 hover:bg-neutral-100 rounded-base transition-colors"
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>
      )}
      {children}
    </aside>
  );
}

