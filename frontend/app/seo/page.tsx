'use client';

import { useState, useEffect } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import StateChip from '@/components/primitives/StateChip';
import EmptyState from '@/components/primitives/EmptyState';
import { CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useBrandStore } from '@/app/_store/brandStore';
import api from '@/lib/api';
import { toast } from '@/lib/toast';

export default function SEOPage() {
  const { selectedBrandId } = useBrandStore();
  const [selectedCluster, setSelectedCluster] = useState(0);
  const [selectedItem, setSelectedItem] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedBrandId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .get('/seo/plans/')
      .then((res) => {
        const plans = res.data.results || res.data || [];
        if (plans.length > 0) {
          const plan = plans[0];
          setClusters(plan.keyword_clusters || []);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load SEO plan');
        setLoading(false);
      });
  }, [selectedBrandId]);

  // Mock data - Surfer-like layout (fallback)
  const [clusters, setClusters] = useState([
    {
      id: 1,
      name: 'Product Features',
      keywords: ['premium quality', 'durable', 'high performance'],
      items: [
        {
          id: 1,
          title: 'Product 1',
          current: { title: 'Product 1', meta: 'Basic description', h1: 'Product 1' },
          proposed: { title: 'Premium Quality Product 1 | Brand Name', meta: 'Shop premium quality Product 1 at Brand Name', h1: 'Premium Quality Product 1' },
        },
      ],
    },
  ]);

  if (!selectedBrandId) {
    return (
      <LayoutShell pageTitle="SEO Optimize" pageSubtitle="Optimize titles, meta tags, and structured data">
        <EmptyState title="No brand selected" description="Please select a brand from the switcher" />
      </LayoutShell>
    );
  }

  if (loading) {
    return (
      <LayoutShell pageTitle="SEO Optimize" pageSubtitle="Optimize titles, meta tags, and structured data">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </LayoutShell>
    );
  }

  if (error) {
    return (
      <LayoutShell pageTitle="SEO Optimize" pageSubtitle="Optimize titles, meta tags, and structured data">
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

  if (clusters.length === 0) {
    return (
      <LayoutShell pageTitle="SEO Optimize" pageSubtitle="Optimize titles, meta tags, and structured data">
        <EmptyState
          title="No SEO plan found"
          description="Generate SEO optimization to get started"
          action={{
            label: 'Generate SEO',
            onClick: () => {
              api
                .post('/seo/generate', { scope: 'all', items: [] })
                .then(() => {
                  toast.success('SEO generation started', 'Check Jobs page for progress');
                })
                .catch((err) => {
                  toast.error('Failed to generate SEO', err.response?.data?.detail);
                });
            },
          }}
        />
      </LayoutShell>
    );
  }

  const currentCluster = clusters[selectedCluster];
  const currentItem = currentCluster.items[selectedItem];

  const score = 85;
  const checklist = [
    { label: 'Title length (50-60 chars)', status: 'pass' },
    { label: 'Meta description (150-160 chars)', status: 'pass' },
    { label: 'H1 present and unique', status: 'pass' },
    { label: 'Keyword density (1-2%)', status: 'warning' },
    { label: 'Internal links (3-5)', status: 'fail' },
    { label: 'JSON-LD structured data', status: 'pass' },
  ];

  return (
    <LayoutShell
      pageTitle="SEO Optimize"
      pageSubtitle="Optimize titles, meta tags, and structured data"
      rightPanelContent={
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold mb-3">SEO Score</h3>
            <div className="text-4xl font-bold text-primary-600 mb-2">{score}</div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: `${score}%` }}
              />
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Checklist</h3>
            <div className="space-y-2">
              {checklist.map((item, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  {item.status === 'pass' && <CheckCircle2 className="w-4 h-4 text-accent-emerald" />}
                  {item.status === 'warning' && <AlertCircle className="w-4 h-4 text-accent-amber" />}
                  {item.status === 'fail' && <XCircle className="w-4 h-4 text-accent-rose" />}
                  <span className={item.status === 'fail' ? 'text-neutral-600 line-through' : ''}>
                    {item.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      }
    >
      <div className="grid grid-cols-12 gap-6">
        {/* Left: Cluster List */}
        <div className="col-span-3">
          <div className="bg-white rounded-lg border border-neutral-200 p-4">
            <h3 className="font-semibold mb-3">Keyword Clusters</h3>
            <div className="space-y-2">
              {clusters.map((cluster, index) => (
                <button
                  key={cluster.id}
                  onClick={() => {
                    setSelectedCluster(index);
                    setSelectedItem(0);
                  }}
                  className={`w-full text-left p-3 rounded-base transition-colors ${
                    selectedCluster === index
                      ? 'bg-primary-50 text-primary-700 border border-primary-200'
                      : 'hover:bg-neutral-50 border border-transparent'
                  }`}
                >
                  <div className="font-medium text-sm mb-1">{cluster.name}</div>
                  <div className="text-xs text-neutral-600">
                    {cluster.keywords.slice(0, 2).join(', ')}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Center: Fields Editor */}
        <div className="col-span-6">
          <div className="bg-white rounded-lg border border-neutral-200 p-6 space-y-6">
            <div>
              <h3 className="font-semibold mb-4">Current Item</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Title</label>
                  <input
                    type="text"
                    value={currentItem.proposed.title}
                    className="w-full px-4 py-2 border border-neutral-200 rounded-base focus:outline-none focus:ring-2 focus:ring-primary-600"
                    readOnly
                  />
                  <p className="text-xs text-neutral-500 mt-1">
                    {currentItem.proposed.title.length} characters
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Meta Description</label>
                  <textarea
                    value={currentItem.proposed.meta}
                    rows={3}
                    className="w-full px-4 py-2 border border-neutral-200 rounded-base focus:outline-none focus:ring-2 focus:ring-primary-600"
                    readOnly
                  />
                  <p className="text-xs text-neutral-500 mt-1">
                    {currentItem.proposed.meta.length} characters
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">H1 Tag</label>
                  <input
                    type="text"
                    value={currentItem.proposed.h1}
                    className="w-full px-4 py-2 border border-neutral-200 rounded-base focus:outline-none focus:ring-2 focus:ring-primary-600"
                    readOnly
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </LayoutShell>
  );
}

