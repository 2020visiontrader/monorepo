'use client';

import { useState, useEffect } from 'react';
import LayoutShell from '@/components/layout/LayoutShell';
import StateChip from '@/components/primitives/StateChip';
import EmptyState from '@/components/primitives/EmptyState';
import { RefreshCw, ChevronRight, ChevronDown, Loader2 } from 'lucide-react';
import { useBrandStore } from '@/app/_store/brandStore';
import api, { jobs } from '@/lib/api';
import { toast } from '@/lib/toast';

export default function JobsPage() {
  const { selectedBrandId } = useBrandStore();
  const [expandedJobs, setExpandedJobs] = useState<Set<string>>(new Set());
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jobLogs, setJobLogs] = useState<Record<string, any>>({});

  useEffect(() => {
    if (!selectedBrandId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .get('/jobs/')
      .then((res) => {
        setJobsData(res.data.results || res.data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load jobs');
        setLoading(false);
      });
  }, [selectedBrandId]);

  const loadJobLogs = async (jobId: string) => {
    if (jobLogs[jobId]) return; // Already loaded

    try {
      const res = await jobs.getLogs(jobId);
      setJobLogs((prev) => ({ ...prev, [jobId]: res.data }));
    } catch (err: any) {
      toast.error('Failed to load logs', err.response?.data?.detail);
    }
  };

  // Mock data - GitHub Actions style (fallback)
  const [jobsData, setJobsData] = useState([
    {
      id: 1,
      taskName: 'crawl_competitor_task',
      status: 'success',
      startedAt: '2024-01-15T10:30:00Z',
      completedAt: '2024-01-15T10:32:15Z',
      duration: '2m 15s',
      organization: 'Demo Organization',
      brand: 'Demo Brand',
      logs: [
        { level: 'info', message: 'Starting competitor crawl...', timestamp: '10:30:00' },
        { level: 'info', message: 'Fetching sitemap.xml...', timestamp: '10:30:05' },
        { level: 'info', message: 'Found 8 pages to crawl', timestamp: '10:30:10' },
        { level: 'info', message: 'Crawling page 1/8...', timestamp: '10:30:15' },
        { level: 'info', message: 'Crawling page 2/8...', timestamp: '10:30:20' },
        { level: 'success', message: 'Crawl completed successfully', timestamp: '10:32:15' },
      ],
    },
    {
      id: 2,
      taskName: 'generate_content_task',
      status: 'running',
      startedAt: '2024-01-15T10:35:00Z',
      completedAt: null,
      duration: null,
      organization: 'Demo Organization',
      brand: 'Demo Brand',
      logs: [
        { level: 'info', message: 'Starting content generation...', timestamp: '10:35:00' },
        { level: 'info', message: 'Generating variant 1/3...', timestamp: '10:35:05' },
        { level: 'info', message: 'Generating variant 2/3...', timestamp: '10:35:30' },
      ],
    },
    {
      id: 3,
      taskName: 'publish_to_shopify_task',
      status: 'failure',
      startedAt: '2024-01-15T09:00:00Z',
      completedAt: '2024-01-15T09:01:30Z',
      duration: '1m 30s',
      organization: 'Demo Organization',
      brand: 'Demo Brand',
      error: 'Shopify API rate limit exceeded',
      logs: [
        { level: 'info', message: 'Starting Shopify publish...', timestamp: '09:00:00' },
        { level: 'info', message: 'Publishing 5 products...', timestamp: '09:00:05' },
        { level: 'error', message: 'Shopify API rate limit exceeded', timestamp: '09:01:30' },
      ],
    },
  ]);

  const toggleJob = (id: string) => {
    const newExpanded = new Set(expandedJobs);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
      loadJobLogs(id);
    }
    setExpandedJobs(newExpanded);
  };

  const filteredJobs = selectedStatus === 'all' ? jobsData : jobsData.filter((j: any) => j.status === selectedStatus);

  if (!selectedBrandId) {
    return (
      <LayoutShell pageTitle="Jobs Monitor" pageSubtitle="Track background job status and errors">
        <EmptyState title="No brand selected" description="Please select a brand from the switcher" />
      </LayoutShell>
    );
  }

  if (loading) {
    return (
      <LayoutShell pageTitle="Jobs Monitor" pageSubtitle="Track background job status and errors">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </LayoutShell>
    );
  }

  if (error) {
    return (
      <LayoutShell pageTitle="Jobs Monitor" pageSubtitle="Track background job status and errors">
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

  if (jobsData.length === 0) {
    return (
      <LayoutShell pageTitle="Jobs Monitor" pageSubtitle="Track background job status and errors">
        <EmptyState title="No jobs yet" description="Jobs will appear here when you run background tasks" />
      </LayoutShell>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failure':
        return 'error';
      case 'running':
        return 'info';
      default:
        return 'neutral';
    }
  };

  return (
    <LayoutShell
      pageTitle="Jobs Monitor"
      pageSubtitle="Track background job status and errors"
    >
      <div className="space-y-4">
        {/* Filters */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedStatus('all')}
            className={`px-3 py-1.5 text-sm rounded-base transition-colors ${
              selectedStatus === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setSelectedStatus('success')}
            className={`px-3 py-1.5 text-sm rounded-base transition-colors ${
              selectedStatus === 'success'
                ? 'bg-primary-600 text-white'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
            }`}
          >
            Success
          </button>
          <button
            onClick={() => setSelectedStatus('running')}
            className={`px-3 py-1.5 text-sm rounded-base transition-colors ${
              selectedStatus === 'running'
                ? 'bg-primary-600 text-white'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
            }`}
          >
            Running
          </button>
          <button
            onClick={() => setSelectedStatus('failure')}
            className={`px-3 py-1.5 text-sm rounded-base transition-colors ${
              selectedStatus === 'failure'
                ? 'bg-primary-600 text-white'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
            }`}
          >
            Failed
          </button>
        </div>

        {/* Jobs List - GitHub Actions style */}
        <div className="bg-white rounded-lg border border-neutral-200">
          {filteredJobs.map((job: any) => {
            const logs = jobLogs[job.id];
            return (
              <div key={job.id} className="border-b border-neutral-200 last:border-b-0">
                <div
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-neutral-50 transition-colors"
                  onClick={() => toggleJob(job.id)}
                >
                  <div className="flex items-center gap-3 flex-1">
                    {expandedJobs.has(job.id) ? (
                      <ChevronDown className="w-4 h-4 text-neutral-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-neutral-500" />
                    )}
                    <StateChip label={job.status.toUpperCase()} variant={getStatusColor(job.status)} size="sm" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{job.task_name || job.taskName}</div>
                      <div className="text-xs text-neutral-500">
                        {job.brand || 'Brand'} • {job.started_at || job.startedAt}
                      </div>
                    </div>
                    {job.duration && <div className="text-xs text-neutral-500">{job.duration}</div>}
                    {job.status === 'failure' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toast.info('Retry functionality coming soon');
                        }}
                        className="btn-secondary text-xs flex items-center gap-1"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Retry
                      </button>
                    )}
                  </div>
                </div>

                {expandedJobs.has(job.id) && logs && (
                  <div className="bg-neutral-900 text-neutral-100 p-4 font-mono text-xs overflow-x-auto">
                    {logs.steps?.map((step: any, stepIndex: number) => (
                      <div key={stepIndex} className="mb-4">
                        <div className="text-neutral-400 mb-2">Step: {step.name}</div>
                        {step.lines?.map((log: any, logIndex: number) => (
                          <div
                            key={logIndex}
                            className={`mb-1 ${
                              log.level === 'ERROR'
                                ? 'text-accent-rose'
                                : log.level === 'SUCCESS'
                                ? 'text-accent-emerald'
                                : 'text-neutral-300'
                            }`}
                          >
                            <span className="text-neutral-500 mr-2">{log.ts}</span>
                            <span className="text-neutral-400 mr-2">[{log.level}]</span>
                            {log.msg}
                          </div>
                        ))}
                      </div>
                    ))}
                    {job.error && (
                      <div className="mt-2 pt-2 border-t border-neutral-700 text-accent-rose">
                        Error: {job.error}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </LayoutShell>
  );
}

