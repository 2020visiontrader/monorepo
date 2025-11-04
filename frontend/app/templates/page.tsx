'use client';

import { useState } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import TemplateGrid from '@/components/templates/TemplateGrid';
import EmptyState from '@/components/primitives/EmptyState';

export default function TemplatesPage() {
  const [selectedComplexity, setSelectedComplexity] = useState<string>('all');
  const [selectedSource, setSelectedSource] = useState<string>('all');

  // Mock templates data
  const templates = [
    {
      id: '1',
      name: 'Starter Template',
      description: 'Clean and simple design perfect for getting started',
      complexity: 'Starter' as const,
      source: 'curated' as const,
    },
    {
      id: '2',
      name: 'Sophisticated Template',
      description: 'Advanced template with rich features and customization',
      complexity: 'Sophisticated' as const,
      source: 'curated' as const,
    },
  ];

  const filteredTemplates = templates.filter((t) => {
    if (selectedComplexity !== 'all' && t.complexity !== selectedComplexity) return false;
    if (selectedSource !== 'all' && t.source !== selectedSource) return false;
    return true;
  });

  return (
    <LayoutShell
      pageTitle="Store Templates"
      pageSubtitle="Choose, customize, or generate storefront templates"
    >
      <div className="mb-6 flex justify-between items-center flex-wrap gap-4">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedComplexity('all')}
            className={`px-4 py-2 text-sm font-medium rounded-base transition-colors ${
              selectedComplexity === 'all'
                ? 'bg-neutral-100 text-neutral-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setSelectedComplexity('Starter')}
            className={`px-4 py-2 text-sm font-medium rounded-base transition-colors ${
              selectedComplexity === 'Starter'
                ? 'bg-neutral-100 text-neutral-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            Starter
          </button>
          <button
            onClick={() => setSelectedComplexity('Sophisticated')}
            className={`px-4 py-2 text-sm font-medium rounded-base transition-colors ${
              selectedComplexity === 'Sophisticated'
                ? 'bg-neutral-100 text-neutral-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            Sophisticated
          </button>
          <button
            onClick={() => setSelectedSource('curated')}
            className={`px-4 py-2 text-sm font-medium rounded-base transition-colors ${
              selectedSource === 'curated'
                ? 'bg-neutral-100 text-neutral-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            Curated
          </button>
          <button
            onClick={() => setSelectedSource('generated')}
            className={`px-4 py-2 text-sm font-medium rounded-base transition-colors ${
              selectedSource === 'generated'
                ? 'bg-neutral-100 text-neutral-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            Generated
          </button>
          <button
            onClick={() => setSelectedSource('uploaded')}
            className={`px-4 py-2 text-sm font-medium rounded-base transition-colors ${
              selectedSource === 'uploaded'
                ? 'bg-neutral-100 text-neutral-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            Uploaded
          </button>
        </div>
        <Link href="/templates/generate" className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Generate Template
        </Link>
      </div>

      {filteredTemplates.length > 0 ? (
        <TemplateGrid templates={filteredTemplates} />
      ) : (
        <EmptyState
          title="No templates found"
          description="Try adjusting your filters or generate a new template"
          action={{
            label: 'Generate Template',
            onClick: () => (window.location.href = '/templates/generate'),
          }}
        />
      )}
    </LayoutShell>
  );
}

