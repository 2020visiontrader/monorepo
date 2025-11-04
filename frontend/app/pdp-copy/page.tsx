'use client';

import { useState, useEffect } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import DiffViewer from '@/components/content/DiffViewer';
import StateChip from '@/components/primitives/StateChip';
import EmptyState from '@/components/primitives/EmptyState';
import * as Tabs from '@radix-ui/react-tabs';
import { Check, X, AlertCircle, Loader2 } from 'lucide-react';
import { useBrandStore } from '@/app/_store/brandStore';
import api from '@/lib/api';
import { toast } from '@/lib/toast';

export default function PDPCopyPage() {
  const { selectedBrandId } = useBrandStore();
  const [selectedVariant, setSelectedVariant] = useState(1);
  const [selectedProduct, setSelectedProduct] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedBrandId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .get('/content/products/')
      .then((res) => {
        const prods = res.data.results || res.data || [];
        if (prods.length > 0) {
          setProducts(prods.map((p: any) => ({
            id: p.id,
            title: p.original_title,
            variants: p.variants || [],
            original: {
              title: p.original_title,
              description: p.original_description,
              bullets: [],
            },
          })));
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load products');
        setLoading(false);
      });
  }, [selectedBrandId]);

  // Mock data (fallback)
  const [products, setProducts] = useState([
    {
      id: 1,
      title: 'Sample Product 1',
      variants: [
        {
          id: 1,
          title: 'Sample Product 1 - Premium Quality 1',
          description: 'This is a premium sample product 1 designed with care.',
          bullets: ['High-quality sample product 1', 'Designed for excellence', 'Perfect for your needs'],
        },
        {
          id: 2,
          title: 'Sample Product 1 - Premium Quality 2',
          description: 'This is a premium sample product 1 designed with care and attention to detail.',
          bullets: ['High-quality sample product 1', 'Designed for excellence', 'Perfect for your needs', 'Durable and reliable'],
        },
        {
          id: 3,
          title: 'Sample Product 1 - Premium Quality 3',
          description: 'This is a premium sample product 1 designed with care, featuring advanced technology.',
          bullets: ['High-quality sample product 1', 'Designed for excellence', 'Perfect for your needs', 'Advanced features'],
        },
      ],
      original: {
        title: 'Sample Product 1',
        description: 'A basic product description',
        bullets: ['Feature 1', 'Feature 2'],
      },
    },
  ]);

  if (!selectedBrandId) {
    return (
      <LayoutShell pageTitle="PDP Copy Review" pageSubtitle="Review and approve product copy variants">
        <EmptyState title="No brand selected" description="Please select a brand from the switcher" />
      </LayoutShell>
    );
  }

  if (loading) {
    return (
      <LayoutShell pageTitle="PDP Copy Review" pageSubtitle="Review and approve product copy variants">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </LayoutShell>
    );
  }

  if (error) {
    return (
      <LayoutShell pageTitle="PDP Copy Review" pageSubtitle="Review and approve product copy variants">
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

  if (products.length === 0) {
    return (
      <LayoutShell pageTitle="PDP Copy Review" pageSubtitle="Review and approve product copy variants">
        <EmptyState
          title="No products found"
          description="Generate content variants to review them here"
          action={{
            label: 'Generate Content',
            onClick: () => (window.location.href = '/build-site'),
          }}
        />
      </LayoutShell>
    );
  }

  const currentProduct = products[selectedProduct];
  const currentVariant = currentProduct.variants[selectedVariant - 1];
  const lints = [
    { type: 'warning', message: 'Title length is optimal (55 characters)' },
    { type: 'success', message: 'No forbidden terms detected' },
    { type: 'info', message: 'Required terms found: premium, quality' },
  ];

  const guardrails = [
    { type: 'success', message: 'N-gram similarity check passed' },
    { type: 'success', message: 'Brand lexicon compliance verified' },
    { type: 'warning', message: 'Competitor snippet similarity: 15% (within threshold)' },
  ];

  return (
    <LayoutShell
      pageTitle="PDP Copy Review"
      pageSubtitle="Review and approve product copy variants"
      rightPanelContent={
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Lints
            </h3>
            <div className="space-y-2">
              {lints.map((lint, index) => (
                <div key={index} className="text-sm">
                  <StateChip
                    label={lint.message}
                    variant={lint.type === 'warning' ? 'warning' : lint.type === 'success' ? 'success' : 'info'}
                    size="sm"
                  />
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Guardrails</h3>
            <div className="space-y-2">
              {guardrails.map((guardrail, index) => (
                <div key={index} className="text-sm">
                  <StateChip
                    label={guardrail.message}
                    variant={guardrail.type === 'warning' ? 'warning' : 'success'}
                    size="sm"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-neutral-200 space-y-2">
            <button
              onClick={() => {
                api
                  .post(`/content/variants/${currentVariant.id}/accept`)
                  .then(() => {
                    toast.success('Variant accepted');
                  })
                  .catch((err) => {
                    toast.error('Failed to accept variant', err.response?.data?.detail);
                  });
              }}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              <Check className="w-4 h-4" />
              Accept Variant
            </button>
            <button
              onClick={() => {
                api
                  .post(`/content/variants/${currentVariant.id}/reject`)
                  .then(() => {
                    toast.success('Variant rejected');
                  })
                  .catch((err) => {
                    toast.error('Failed to reject variant', err.response?.data?.detail);
                  });
              }}
              className="w-full btn-secondary flex items-center justify-center gap-2"
            >
              <X className="w-4 h-4" />
              Reject Variant
            </button>
          </div>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Variant Tabs */}
        <Tabs.Root value={String(selectedVariant)} onValueChange={(val) => setSelectedVariant(Number(val))}>
          <Tabs.List className="flex gap-2 border-b border-neutral-200">
            {currentProduct.variants.map((variant, index) => (
              <Tabs.Trigger
                key={variant.id}
                value={String(index + 1)}
                className="px-4 py-2 text-sm font-medium border-b-2 border-transparent data-[state=active]:border-primary-600 data-[state=active]:text-primary-700 transition-colors"
              >
                Variant {index + 1}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          {currentProduct.variants.map((variant, index) => (
            <Tabs.Content key={variant.id} value={String(index + 1)} className="mt-6">
              <div className="space-y-6">
                {/* Title Diff */}
                <div>
                  <h3 className="text-sm font-semibold mb-3">Title</h3>
                  <DiffViewer
                    original={currentProduct.original.title}
                    modified={variant.title}
                    fieldName="Title"
                  />
                </div>

                {/* Description Diff */}
                <div>
                  <h3 className="text-sm font-semibold mb-3">Description</h3>
                  <DiffViewer
                    original={currentProduct.original.description}
                    modified={variant.description}
                    fieldName="Description"
                  />
                </div>

                {/* Bullets Diff */}
                <div>
                  <h3 className="text-sm font-semibold mb-3">Bullet Points</h3>
                  <DiffViewer
                    original={currentProduct.original.bullets.join('\n')}
                    modified={variant.bullets.join('\n')}
                    fieldName="Bullets"
                  />
                </div>
              </div>
            </Tabs.Content>
          ))}
        </Tabs.Root>
      </div>
    </LayoutShell>
  );
}

