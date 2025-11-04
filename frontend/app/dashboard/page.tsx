import LayoutShell from '@/components/layout/LayoutShell';

export default function DashboardPage() {
  return (
    <LayoutShell pageTitle="Dashboard" pageSubtitle="Overview of your brand optimization">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg border border-neutral-200">
          <h3 className="text-lg font-semibold mb-2">Onboarding Status</h3>
          <p className="text-neutral-600">Complete your brand profile</p>
        </div>
        <div className="bg-white p-6 rounded-lg border border-neutral-200">
          <h3 className="text-lg font-semibold mb-2">Competitor Analysis</h3>
          <p className="text-neutral-600">Review competitor insights</p>
        </div>
        <div className="bg-white p-6 rounded-lg border border-neutral-200">
          <h3 className="text-lg font-semibold mb-2">Content Generation</h3>
          <p className="text-neutral-600">Generate product copy</p>
        </div>
      </div>
    </LayoutShell>
  );
}

