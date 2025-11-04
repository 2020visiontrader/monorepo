import LayoutShell from '@/components/layout/LayoutShell';

export default function SettingsPage() {
  return (
    <LayoutShell
      pageTitle="Settings & Pathways"
      pageSubtitle="Configure brand settings and pathways"
    >
      <div className="bg-white p-6 rounded-lg border border-neutral-200">
        <h3 className="text-lg font-semibold mb-4">Pathways</h3>
        <p className="text-neutral-600">Create and manage playbooks for your brand</p>
      </div>
    </LayoutShell>
  );
}

