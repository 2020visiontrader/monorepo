'use client';

import { useState } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import Link from 'next/link';

export default function GenerateTemplatePage() {
  const [complexity, setComplexity] = useState('Starter');
  const [industry, setIndustry] = useState('');

  return (
    <LayoutShell
      pageTitle="Generate Template"
      pageSubtitle="Create a custom store template with AI"
    >
      <div className="max-w-2xl mx-auto">
        <div className="bg-white p-8 rounded-lg border border-neutral-200">
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Complexity</label>
            <div className="flex gap-4">
              <button
                onClick={() => setComplexity('Starter')}
                className={`flex-1 px-4 py-3 rounded-base border transition-colors ${
                  complexity === 'Starter'
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-neutral-200 hover:border-neutral-300'
                }`}
              >
                Starter
              </button>
              <button
                onClick={() => setComplexity('Sophisticated')}
                className={`flex-1 px-4 py-3 rounded-base border transition-colors ${
                  complexity === 'Sophisticated'
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-neutral-200 hover:border-neutral-300'
                }`}
              >
                Sophisticated
              </button>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Industry</label>
            <input
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="e.g., Fashion, Electronics, Home & Garden"
              className="w-full px-4 py-2 border border-neutral-200 rounded-base focus:outline-none focus:ring-2 focus:ring-primary-600"
            />
          </div>

          <div className="flex gap-4">
            <Link href="/templates" className="btn-secondary">
              Cancel
            </Link>
            <button className="btn-primary">Generate Template</button>
          </div>
        </div>
      </div>
    </LayoutShell>
  );
}

