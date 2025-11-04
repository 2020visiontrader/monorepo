'use client';

import { useState, useEffect } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import StateChip from '@/components/primitives/StateChip';
import EmptyState from '@/components/primitives/EmptyState';
import { RefreshCw, Loader2 } from 'lucide-react';
import { useBrandStore } from '@/app/_store/brandStore';
import api, { competitors } from '@/lib/api';
import { toast } from '@/lib/toast';

export default function CompetitorsPage() {
  const { selectedBrandId } = useBrandStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [maxPages, setMaxPages] = useState(10);
  const [pagesCrawled, setPagesCrawled] = useState(0);

  useEffect(() => {
    if (!selectedBrandId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .get('/competitors/insights')
      .then((res) => {
        setInsights(res.data.insights || []);
        setPagesCrawled(res.data.insights?.[0]?.pages_crawled || 0);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load insights');
        setLoading(false);
      });

    // Get brand profile for single_sku
    api
      .get(`/brands/${selectedBrandId}/profile`)
      .then((res) => {
        setMaxPages(res.data.single_sku ? 5 : 10);
      })
      .catch(() => {});
  }, [selectedBrandId]);

  const handleRecrawl = () => {
    if (!insights.length || !selectedBrandId) return;
    const competitorId = insights[0].competitor_id;
    competitors
      .recrawl(competitorId, { force: true })
      .then(() => {
        toast.success('Recrawl started', 'Check Jobs page for progress');
      })
      .catch((err) => {
        toast.error('Failed to start recrawl', err.response?.data?.detail);
      });
  };

  if (!selectedBrandId) {
    return (
      <LayoutShell
        pageTitle="Competitor Insights"
        pageSubtitle="Analyze competitor websites and strategies"
      >
        <EmptyState
          title="No brand selected"
          description="Please select a brand from the switcher"
        />
      </LayoutShell>
    );
  }

  if (loading) {
    return (
      <LayoutShell
        pageTitle="Competitor Insights"
        pageSubtitle="Analyze competitor websites and strategies"
      >
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </LayoutShell>
    );
  }

  if (error) {
    return (
      <LayoutShell
        pageTitle="Competitor Insights"
        pageSubtitle="Analyze competitor websites and strategies"
      >
        <div className="bg-accent-rose/10 border border-accent-rose/20 rounded-base p-6">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-accent-rose">Error</h3>
          </div>
          <p className="text-sm text-neutral-700 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            Try Again
          </button>
        </div>
      </LayoutShell>
    );
  }

  if (insights.length === 0) {
    return (
      <LayoutShell
        pageTitle="Competitor Insights"
        pageSubtitle="Analyze competitor websites and strategies"
      >
        <EmptyState
          title="No competitors added"
          description="Add competitor URLs to start analyzing"
          action={{
            label: 'Start Onboarding',
            onClick: () => (window.location.href = '/onboarding'),
          }}
        />
      </LayoutShell>
    );
  }

  return (
    <LayoutShell
      pageTitle="Competitor Insights"
      pageSubtitle="Analyze competitor websites and strategies"
    >
      <div className="space-y-6">
        {/* Header with recrawl and caps */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <StateChip label={`${pagesCrawled}/${maxPages} pages crawled`} variant="info" />
            <button
              onClick={handleRecrawl}
              className="btn-secondary flex items-center gap-2 text-sm"
            >
              <RefreshCw className="w-4 h-4" />
              Recrawl
            </button>
          </div>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg border border-neutral-200">
            <h3 className="text-lg font-semibold mb-4">Information Architecture</h3>
            <div className="space-y-2 text-sm">
              <div>
                <p className="font-medium text-neutral-700 mb-1">Navigation</p>
                <ul className="text-neutral-600 space-y-1">
                  <li>• Home</li>
                  <li>• Products</li>
                  <li>• About</li>
                  <li>• Contact</li>
                </ul>
              </div>
              <div className="pt-2 border-t border-neutral-200">
                <p className="font-medium text-neutral-700 mb-1">Taxonomy</p>
                <p className="text-neutral-600">3 main categories identified</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-neutral-200">
            <h3 className="text-lg font-semibold mb-4">Tone & Messaging</h3>
            <div className="space-y-2 text-sm">
              <div>
                <p className="font-medium text-neutral-700 mb-1">Tone Analysis</p>
                <div className="flex gap-2 flex-wrap">
                  <StateChip label="Professional: 85%" variant="info" size="sm" />
                  <StateChip label="Friendly: 70%" variant="info" size="sm" />
                </div>
              </div>
              <div className="pt-2 border-t border-neutral-200">
                <p className="font-medium text-neutral-700 mb-1">Key Phrases</p>
                <p className="text-neutral-600">"Premium quality", "Customer-focused", "Innovative"</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-neutral-200">
            <h3 className="text-lg font-semibold mb-4">Keyword Seeds</h3>
            <div className="space-y-2 text-sm">
              <p className="font-medium text-neutral-700 mb-2">Top Keywords</p>
              <div className="flex flex-wrap gap-2">
                {['premium', 'quality', 'durable', 'performance', 'innovative'].map((keyword) => (
                  <StateChip key={keyword} label={keyword} variant="neutral" size="sm" />
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-neutral-200">
            <h3 className="text-lg font-semibold mb-4">Section Patterns</h3>
            <div className="space-y-2 text-sm">
              <p className="font-medium text-neutral-700 mb-2">Common Sections</p>
              <ul className="text-neutral-600 space-y-1">
                <li>• Hero with CTA</li>
                <li>• Features grid (3 columns)</li>
                <li>• Product showcase</li>
                <li>• Testimonials carousel</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </LayoutShell>
  );
}

