'use client';

import { useState } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import Link from 'next/link';
import DeviceToggle from '@/components/templates/DeviceToggle';
import PreviewFrame from '@/components/templates/PreviewFrame';

export default function TemplatePreviewPage({ params }: { params: { templateId: string } }) {
  const [device, setDevice] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [enabledSections, setEnabledSections] = useState({
    hero: true,
    features: true,
    products: true,
    testimonials: false,
  });

  const toggleSection = (section: keyof typeof enabledSections) => {
    setEnabledSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <LayoutShell
      pageTitle="Template Preview"
      pageSubtitle="Preview and customize template"
      rightPanelContent={
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold mb-4">Overview</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-neutral-600 mb-1">Complexity</p>
                <p className="font-medium">Starter</p>
              </div>
              <div>
                <p className="text-sm text-neutral-600 mb-1">Source</p>
                <p className="font-medium">Curated</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Sections</h3>
            <div className="space-y-2">
              {Object.entries(enabledSections).map(([key, enabled]) => (
                <label key={key} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={() => toggleSection(key as keyof typeof enabledSections)}
                    className="rounded"
                  />
                  <span className="text-sm capitalize">{key}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Theme Tokens</h3>
            <div className="text-sm space-y-2 text-neutral-600">
              <p>Primary: #6366f1</p>
              <p>Font: Inter</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Compatibility</h3>
            <div className="text-sm space-y-1 text-neutral-600">
              <p>✓ Shopify Sections</p>
              <p>✓ OS 2.0 Features</p>
            </div>
          </div>
        </div>
      }
    >
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <DeviceToggle value={device} onChange={setDevice} />
          <div className="flex gap-4">
            <Link href="/templates" className="btn-secondary">
              Back
            </Link>
            <Link href={`/templates/${params.templateId}/customize`} className="btn-primary">
              Customize
            </Link>
          </div>
        </div>

        <PreviewFrame device={device}>
          <div className="w-full h-full p-8 space-y-8">
            {enabledSections.hero && (
              <div className="border border-dashed border-neutral-300 rounded-base p-8 text-center bg-neutral-50">
                <h4 className="font-medium text-neutral-700">Hero Section</h4>
              </div>
            )}
            {enabledSections.features && (
              <div className="border border-dashed border-neutral-300 rounded-base p-8 text-center bg-neutral-50">
                <h4 className="font-medium text-neutral-700">Features Section</h4>
              </div>
            )}
            {enabledSections.products && (
              <div className="border border-dashed border-neutral-300 rounded-base p-8 text-center bg-neutral-50">
                <h4 className="font-medium text-neutral-700">Products Section</h4>
              </div>
            )}
            {enabledSections.testimonials && (
              <div className="border border-dashed border-neutral-300 rounded-base p-8 text-center bg-neutral-50">
                <h4 className="font-medium text-neutral-700">Testimonials</h4>
              </div>
            )}
          </div>
        </PreviewFrame>
      </div>
    </LayoutShell>
  );
}

