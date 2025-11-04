'use client';

import TemplateCard from './TemplateCard';

interface Template {
  id: string;
  name: string;
  description: string;
  complexity: 'Starter' | 'Sophisticated';
  source: 'curated' | 'generated' | 'uploaded';
  previewImageUrl?: string;
}

interface TemplateGridProps {
  templates: Template[];
  onTemplateClick?: (id: string) => void;
}

export default function TemplateGrid({ templates, onTemplateClick }: TemplateGridProps) {
  if (templates.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {templates.map((template) => (
        <TemplateCard key={template.id} {...template} />
      ))}
    </div>
  );
}

