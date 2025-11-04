'use client';

interface StateChipProps {
  label: string;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
}

export default function StateChip({ label, variant = 'neutral', size = 'md' }: StateChipProps) {
  const variants = {
    success: 'bg-accent-emerald/10 text-accent-emerald border-accent-emerald/20',
    warning: 'bg-accent-amber/10 text-accent-amber border-accent-amber/20',
    error: 'bg-accent-rose/10 text-accent-rose border-accent-rose/20',
    info: 'bg-primary-50 text-primary-700 border-primary-200',
    neutral: 'bg-neutral-100 text-neutral-700 border-neutral-200',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-base border ${variants[variant]} ${sizes[size]}`}
    >
      {label}
    </span>
  );
}

