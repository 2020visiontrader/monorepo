'use client';

import { useState, useEffect } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import StateChip from '@/components/primitives/StateChip';
import EmptyState from '@/components/primitives/EmptyState';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { useBrandStore } from '@/app/_store/brandStore';
import { brands, shopify } from '@/lib/api';
import { toast } from '@/lib/toast';

export default function OnboardingPage() {
  const { selectedBrandId } = useBrandStore();
  const [step, setStep] = useState(1);
  const totalSteps = 5;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    mission: '',
    categories: [] as string[],
    tone: { professional: 0.5, friendly: 0.5 },
    requiredTerms: [] as string[],
    competitors: [] as string[],
    shopifyConnected: false,
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [shopifyStatus, setShopifyStatus] = useState<any>(null);

  useEffect(() => {
    if (!selectedBrandId) {
      setLoading(false);
      setError('Please select a brand');
      return;
    }

    setLoading(true);
    brands
      .getProfile(selectedBrandId)
      .then((res) => {
        const profile = res.data;
        setFormData({
          mission: profile.mission || '',
          categories: profile.categories || [],
          tone: profile.tone_sliders || { professional: 0.5, friendly: 0.5 },
          requiredTerms: profile.required_terms || [],
          competitors: [],
          shopifyConnected: !!profile.shopify_store,
        });
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load profile');
        setLoading(false);
      });

    shopify
      .getConnection(selectedBrandId)
      .then((res) => {
        setShopifyStatus(res.data);
      })
      .catch(() => {
        // Ignore errors
      });
  }, [selectedBrandId]);

  const validateStep = (stepNum: number): boolean => {
    const errors: Record<string, string> = {};
    if (stepNum === 1 && !formData.mission) {
      errors.mission = 'Mission is required';
    }
    if (stepNum === 3 && formData.competitors.length === 0) {
      errors.competitors = 'At least one competitor is required';
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      if (step === totalSteps) {
        // Save profile
        if (!selectedBrandId) return;
        brands
          .updateProfile(selectedBrandId, formData)
          .then(() => {
            toast.success('Profile saved successfully');
            setStep(Math.min(totalSteps, step + 1));
          })
          .catch((err) => {
            toast.error('Failed to save profile', err.response?.data?.detail);
          });
      } else {
        setStep(Math.min(totalSteps, step + 1));
      }
    }
  };

  if (!selectedBrandId) {
    return (
      <LayoutShell pageTitle="Brand Onboarding" pageSubtitle="Set up your brand profile">
        <EmptyState
          title="No brand selected"
          description="Please select a brand from the switcher in the top navigation"
        />
      </LayoutShell>
    );
  }

  if (loading) {
    return (
      <LayoutShell pageTitle="Brand Onboarding" pageSubtitle="Set up your brand profile">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </LayoutShell>
    );
  }

  if (error) {
    return (
      <LayoutShell pageTitle="Brand Onboarding" pageSubtitle="Set up your brand profile">
        <div className="bg-accent-rose/10 border border-accent-rose/20 rounded-base p-6">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-accent-rose" />
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

  return (
    <LayoutShell
      pageTitle="Brand Onboarding"
      pageSubtitle="Set up your brand profile"
      rightPanelContent={
        <div className="space-y-4">
          <h3 className="font-semibold mb-3">Summary</h3>
          <div className="space-y-3 text-sm">
            <div>
              <p className="text-xs text-neutral-500 mb-1">Mission</p>
              <p className="text-neutral-700">
                {formData.mission || <span className="text-neutral-400">Not set</span>}
              </p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Categories</p>
              <div className="flex flex-wrap gap-1">
                {formData.categories.length > 0 ? (
                  formData.categories.map((cat) => (
                    <StateChip key={cat} label={cat} size="sm" />
                  ))
                ) : (
                  <span className="text-neutral-400">None</span>
                )}
              </div>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Competitors</p>
              <p className="text-neutral-700">{formData.competitors.length} added</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Shopify</p>
              {formData.shopifyConnected ? (
                <StateChip label="Connected" variant="success" size="sm" />
              ) : (
                <StateChip label="Not connected" variant="neutral" size="sm" />
              )}
            </div>
          </div>
        </div>
      }
    >
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div
                key={i + 1}
                className={`flex-1 h-2 mx-1 rounded-full ${
                  i + 1 <= step ? 'bg-primary-600' : 'bg-neutral-200'
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-neutral-600">
            Step {step} of {totalSteps}
          </p>
        </div>

        <div className="bg-white p-8 rounded-lg border border-neutral-200">
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Basics</h2>
              <p className="text-neutral-600 mb-6">Tell us about your brand</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Mission Statement <span className="text-accent-rose">*</span>
                  </label>
                  <textarea
                    value={formData.mission}
                    onChange={(e) => setFormData({ ...formData, mission: e.target.value })}
                    rows={4}
                    className={`w-full px-4 py-2 border rounded-base focus:outline-none focus:ring-2 focus:ring-primary-600 ${
                      validationErrors.mission ? 'border-accent-rose' : 'border-neutral-200'
                    }`}
                    placeholder="Describe your brand's mission and values..."
                  />
                  {validationErrors.mission && (
                    <p className="mt-1 text-xs text-accent-rose flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {validationErrors.mission}
                    </p>
                  )}
                  {formData.mission && !validationErrors.mission && (
                    <p className="mt-1 text-xs text-accent-emerald flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      Looks good!
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
          {step === 2 && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Tone & Lexicon</h2>
              <p className="text-neutral-600 mb-6">Define your brand voice</p>
              {/* Form fields here */}
            </div>
          )}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Competitors</h2>
              <p className="text-neutral-600 mb-6">Add competitor URLs</p>
              {/* Form fields here */}
            </div>
          )}
          {step === 4 && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Shopify Connect</h2>
              <p className="text-neutral-600 mb-6">Connect your Shopify store</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Connection Status</label>
                  {shopifyStatus ? (
                    <div className="flex items-center gap-3">
                      <StateChip
                        label={shopifyStatus.connected ? 'Connected' : 'Not Connected'}
                        variant={shopifyStatus.connected ? 'success' : 'neutral'}
                      />
                      {shopifyStatus.shop && (
                        <span className="text-sm text-neutral-600">{shopifyStatus.shop}</span>
                      )}
                    </div>
                  ) : (
                    <StateChip label="Not Connected" variant="neutral" />
                  )}
                </div>
                <div className="flex gap-4">
                  <button
                    className="btn-primary"
                    disabled={process.env.NEXT_PUBLIC_ENV === 'ST'}
                    title={process.env.NEXT_PUBLIC_ENV === 'ST' ? 'Mocked in ST' : ''}
                  >
                    Connect
                  </button>
                  {shopifyStatus?.connected && (
                    <button
                      onClick={() => {
                        if (!selectedBrandId) return;
                        shopify
                          .disconnect(selectedBrandId)
                          .then(() => {
                            toast.success('Disconnected successfully');
                            setShopifyStatus({ ...shopifyStatus, connected: false });
                          })
                          .catch((err) => {
                            toast.error('Failed to disconnect', err.response?.data?.detail);
                          });
                      }}
                      className="btn-secondary"
                    >
                      Disconnect
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
          {step === 5 && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Review & Confirm</h2>
              <p className="text-neutral-600 mb-6">Review your settings</p>
              {/* Summary here */}
            </div>
          )}

          <div className="flex justify-between mt-8">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="btn-secondary disabled:opacity-50"
            >
              Previous
            </button>
            <button onClick={handleNext} className="btn-primary">
              {step === totalSteps ? 'Complete' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </LayoutShell>
  );
}

