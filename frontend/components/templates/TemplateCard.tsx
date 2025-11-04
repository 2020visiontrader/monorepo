'use client';

import Link from 'next/link';
import StateChip from '../primitives/StateChip';

interface TemplateCardProps {
  id: string;
  name: string;
  description: string;
  complexity: 'Starter' | 'Sophisticated';
  source: 'curated' | 'generated' | 'uploaded';
  previewImageUrl?: string;
}

export default function TemplateCard({
  id,
  name,
  description,
  complexity,
  source,
  previewImageUrl,
}: TemplateCardProps) {
  const sourceLabels = {
    curated: 'Curated',
    generated: 'Generated',
    uploaded: 'Uploaded',
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-neutral-200 hover:shadow-layered transition-shadow">
      <div className="aspect-video bg-neutral-100 rounded-base mb-4 overflow-hidden">
        {previewImageUrl ? (
          <img src={previewImageUrl} alt={name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-neutral-400 text-sm">No preview</span>
          </div>
        )}
      </div>
      <div className="mb-3">
        <h3 className="font-semibold text-base mb-1">{name}</h3>
        <p className="text-sm text-neutral-600 line-clamp-2">{description}</p>
      </div>
      <div className="flex items-center gap-2 mb-4">
        <StateChip label={complexity} variant="info" size="sm" />
        <StateChip label={sourceLabels[source]} variant="neutral" size="sm" />
      </div>
      <div className="flex gap-2">
        <Link
          href={`/templates/${id}`}
          className="flex-1 btn-secondary text-sm text-center"
        >
          Preview
        </Link>
        <Link
          href={`/templates/${id}/customize`}
          className="flex-1 btn-primary text-sm text-center"
        >
          Use
        </Link>
      </div>
    </div>
  );
}

