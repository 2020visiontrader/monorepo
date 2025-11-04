'use client';

import { Monitor, Tablet, Smartphone } from 'lucide-react';

type Device = 'desktop' | 'tablet' | 'mobile';

interface DeviceToggleProps {
  value: Device;
  onChange: (device: Device) => void;
}

export default function DeviceToggle({ value, onChange }: DeviceToggleProps) {
  return (
    <div className="flex gap-2">
      <button
        onClick={() => onChange('desktop')}
        className={`p-2 rounded-base transition-colors ${
          value === 'desktop' ? 'bg-primary-100 text-primary-700' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
        }`}
        aria-label="Desktop view"
      >
        <Monitor className="w-5 h-5" />
      </button>
      <button
        onClick={() => onChange('tablet')}
        className={`p-2 rounded-base transition-colors ${
          value === 'tablet' ? 'bg-primary-100 text-primary-700' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
        }`}
        aria-label="Tablet view"
      >
        <Tablet className="w-5 h-5" />
      </button>
      <button
        onClick={() => onChange('mobile')}
        className={`p-2 rounded-base transition-colors ${
          value === 'mobile' ? 'bg-primary-100 text-primary-700' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
        }`}
        aria-label="Mobile view"
      >
        <Smartphone className="w-5 h-5" />
      </button>
    </div>
  );
}

