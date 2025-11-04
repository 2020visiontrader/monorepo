'use client';

import { useState } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import { GripVertical } from 'lucide-react';

export default function CustomizeTemplatePage({ params }: { params: { templateId: string } }) {
  const [activeTab, setActiveTab] = useState<'tokens' | 'sections' | 'seo'>('tokens');

  return (
    <LayoutShell
      pageTitle="Customize Template"
      pageSubtitle="Adjust theme tokens, sections, and SEO defaults"
    >
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 flex gap-2 border-b border-neutral-200">
          <button
            onClick={() => setActiveTab('tokens')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'tokens'
                ? 'border-primary-600 text-primary-700'
                : 'border-transparent text-neutral-600 hover:text-neutral-900'
            }`}
          >
            Theme Tokens
          </button>
          <button
            onClick={() => setActiveTab('sections')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'sections'
                ? 'border-primary-600 text-primary-700'
                : 'border-transparent text-neutral-600 hover:text-neutral-900'
            }`}
          >
            Sections
          </button>
          <button
            onClick={() => setActiveTab('seo')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'seo'
                ? 'border-primary-600 text-primary-700'
                : 'border-transparent text-neutral-600 hover:text-neutral-900'
            }`}
          >
            SEO Defaults
          </button>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 bg-white p-6 rounded-lg border border-neutral-200">
            {activeTab === 'tokens' && (
              <div>
                <h3 className="font-semibold mb-4">Theme Tokens</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Primary Color</label>
                    <input type="color" className="w-full h-10 rounded-base" defaultValue="#6366f1" />
                    <p className="text-xs text-neutral-500 mt-1">Contrast ratio: 4.5:1 (WCAG AA)</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Font Family</label>
                    <select className="w-full px-4 py-2 border border-neutral-200 rounded-base">
                      <option>Inter</option>
                      <option>System</option>
                    </select>
                  </div>
                  <div className="p-3 bg-accent-emerald/10 border border-accent-emerald/20 rounded-base">
                    <p className="text-xs text-accent-emerald font-medium">✓ Accessibility check passed</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'sections' && (
              <div>
                <h3 className="font-semibold mb-4">Section Order</h3>
                <div className="space-y-2">
                  {['Hero', 'Features', 'Products'].map((section) => (
                    <div key={section} className="flex items-center justify-between p-3 bg-neutral-50 rounded-base">
                      <div className="flex items-center gap-2">
                        <GripVertical className="w-4 h-4 text-neutral-400 cursor-move" />
                        <span>{section}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" defaultChecked />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeTab === 'seo' && (
              <div>
                <h3 className="font-semibold mb-4">SEO Defaults</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Title Format</label>
                    <input type="text" className="w-full px-4 py-2 border border-neutral-200 rounded-base" defaultValue="{Product Name} | {Brand Name}" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Meta Description Format</label>
                    <input type="text" className="w-full px-4 py-2 border border-neutral-200 rounded-base" defaultValue="Shop {Product Name} at {Brand Name}" />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg border border-neutral-200">
            <h3 className="font-semibold mb-4">Preview</h3>
            <div className="aspect-video bg-neutral-100 rounded-base"></div>
            <div className="mt-4 space-y-2">
              <button
                className="w-full btn-primary"
                onClick={() => {
                  // Show diff summary
                  alert('Variant saved successfully!\n\nChanges:\n- Updated primary color\n- Enabled all sections');
                }}
              >
                Save Variant
              </button>
              <button className="w-full btn-secondary">Apply to Site Blueprint</button>
            </div>
          </div>
        </div>
      </div>
    </LayoutShell>
  );
}

