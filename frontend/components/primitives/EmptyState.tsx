'use client';

import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {Icon && (
        <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center mb-4">
          <Icon className="w-6 h-6 text-neutral-400" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-neutral-900 mb-2">{title}</h3>
      {description && <p className="text-sm text-neutral-600 text-center max-w-md mb-6">{description}</p>}
      {action && (
        <button onClick={action.onClick} className="btn-primary">
          {action.label}
        </button>
      )}
    </div>
  );
}

