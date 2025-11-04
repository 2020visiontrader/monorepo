import LayoutShell from '@/components/layout/LayoutShell';

export default function FrameworksPage() {
  return (
    <LayoutShell
      pageTitle="Frameworks Curation"
      pageSubtitle="Manage marketing framework library"
    >
      <div className="bg-white p-6 rounded-lg border border-neutral-200">
        <h3 className="text-lg font-semibold mb-4">Framework Library</h3>
        <p className="text-neutral-600">Review and approve framework candidates</p>
      </div>
    </LayoutShell>
  );
}

