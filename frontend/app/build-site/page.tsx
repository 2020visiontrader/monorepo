'use client';

import { useState, useEffect } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import PreviewFrame from '@/components/templates/PreviewFrame';
import EmptyState from '@/components/primitives/EmptyState';
import { GripVertical, Loader2 } from 'lucide-react';
import { useBrandStore } from '@/app/_store/brandStore';
import { brands } from '@/lib/api';
import { toast } from '@/lib/toast';
import api from '@/lib/api';

export default function BuildSitePage() {
  const { selectedBrandId } = useBrandStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [blueprint, setBlueprint] = useState<any>(null);
  const [sections, setSections] = useState([
    { id: 1, name: 'Hero Section', enabled: true, order: 1 },
    { id: 2, name: 'Features Section', enabled: true, order: 2 },
    { id: 3, name: 'Products Section', enabled: true, order: 3 },
    { id: 4, name: 'Testimonials', enabled: false, order: 4 },
  ]);

  useEffect(() => {
    if (!selectedBrandId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    brands
      .getBlueprint(selectedBrandId)
      .then((res) => {
        setBlueprint(res.data);
        if (res.data.json?.sections) {
          setSections(
            res.data.json.sections.map((s: any, idx: number) => ({
              id: idx + 1,
              name: s.name || s.key,
              enabled: s.enabled !== false,
              order: idx + 1,
            }))
          );
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load blueprint');
        setLoading(false);
      });
  }, [selectedBrandId]);

  const toggleSection = (id: number) => {
    const updated = sections.map((s) => (s.id === id ? { ...s, enabled: !s.enabled } : s));
    setSections(updated);
    
    // Update blueprint
    if (selectedBrandId) {
      const sectionKey = sections.find((s) => s.id === id)?.name.toLowerCase().replace(' ', '-');
      brands
        .mutateBlueprintSection(selectedBrandId, 'disable', sectionKey || '')
        .then(() => {
          toast.success('Blueprint updated');
        })
        .catch((err) => {
          toast.error('Failed to update blueprint', err.response?.data?.detail);
        });
    }
  };

  if (!selectedBrandId) {
    return (
      <LayoutShell pageTitle="Build My Site" pageSubtitle="Review and customize your site blueprint">
        <EmptyState title="No brand selected" description="Please select a brand from the switcher" />
      </LayoutShell>
    );
  }

  if (loading) {
    return (
      <LayoutShell pageTitle="Build My Site" pageSubtitle="Review and customize your site blueprint">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </LayoutShell>
    );
  }

  if (error) {
    return (
      <LayoutShell pageTitle="Build My Site" pageSubtitle="Review and customize your site blueprint">
        <div className="bg-accent-rose/10 border border-accent-rose/20 rounded-base p-6">
          <h3 className="font-semibold text-accent-rose mb-2">Error</h3>
          <p className="text-sm text-neutral-700 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            Try Again
          </button>
        </div>
      </LayoutShell>
    );
  }

  if (!blueprint && sections.length === 0) {
    return (
      <LayoutShell pageTitle="Build My Site" pageSubtitle="Review and customize your site blueprint">
        <EmptyState
          title="No blueprint found"
          description="Generate a site blueprint to get started"
          action={{
            label: 'Generate Blueprint',
            onClick: () => {
              if (!selectedBrandId) return;
              import('@/lib/api').then(({ default: api }) => {
                api
                  .post(`/brands/${selectedBrandId}/blueprint/generate`)
                  .then(() => {
                    toast.success('Blueprint generation started', 'Check Jobs page for progress');
                  })
                  .catch((err) => {
                    toast.error('Failed to generate blueprint', err.response?.data?.detail);
                  });
              });
            },
          }}
        />
      </LayoutShell>
    );
  }

  return (
    <LayoutShell
      pageTitle="Build My Site"
      pageSubtitle="Review and customize your site blueprint"
      rightPanelContent={
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold mb-3">Properties</h3>
            <div className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-medium text-neutral-600 mb-1">Navigation Style</label>
                <select className="w-full px-3 py-2 border border-neutral-200 rounded-base text-sm">
                  <option>Horizontal</option>
                  <option>Vertical</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-neutral-600 mb-1">Layout</label>
                <select className="w-full px-3 py-2 border border-neutral-200 rounded-base text-sm">
                  <option>Full Width</option>
                  <option>Container</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      }
    >
      <div className="grid grid-cols-12 gap-6">
        {/* Left: Sections List */}
        <div className="col-span-3">
          <div className="bg-white rounded-lg border border-neutral-200 p-4">
            <h3 className="font-semibold mb-4">Sections</h3>
            <div className="space-y-2">
              {sections
                .sort((a, b) => a.order - b.order)
                .map((section) => (
                  <div
                    key={section.id}
                    className="flex items-center gap-2 p-2 rounded-base hover:bg-neutral-50 border border-transparent hover:border-neutral-200"
                  >
                    <GripVertical className="w-4 h-4 text-neutral-400 cursor-move" />
                    <label className="flex items-center gap-2 flex-1 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={section.enabled}
                        onChange={() => toggleSection(section.id)}
                        className="rounded"
                      />
                      <span className="text-sm">{section.name}</span>
                    </label>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Center: Template Preview */}
        <div className="col-span-6">
          <PreviewFrame device="desktop">
            <div className="w-full h-full p-8 space-y-8">
              {sections
                .filter((s) => s.enabled)
                .map((section) => (
                  <div
                    key={section.id}
                    className="border border-dashed border-neutral-300 rounded-base p-8 text-center bg-neutral-50"
                  >
                    <h4 className="font-medium text-neutral-700">{section.name}</h4>
                    <p className="text-sm text-neutral-500 mt-2">Preview content</p>
                  </div>
                ))}
            </div>
          </PreviewFrame>
        </div>
      </div>
    </LayoutShell>
  );
}

