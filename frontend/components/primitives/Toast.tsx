'use client';

import * as ToastPrimitive from '@radix-ui/react-toast';
import { X } from 'lucide-react';
import { useToast } from '@/lib/toast';

interface ToastProps {
  id: string;
  title: string;
  description?: string;
  variant?: 'success' | 'error' | 'info';
}

export function Toast({ id, title, description, variant = 'info' }: ToastProps) {
  const { remove } = useToast();
  const variants = {
    success: 'bg-accent-emerald/10 border-accent-emerald text-accent-emerald',
    error: 'bg-accent-rose/10 border-accent-rose text-accent-rose',
    info: 'bg-primary-50 border-primary-200 text-primary-700',
  };

  return (
    <ToastPrimitive.Root
      onOpenChange={(open) => {
        if (!open) {
          setTimeout(() => remove(id), 300);
        }
      }}
      className={`${variants[variant]} border rounded-base p-4 shadow-layered flex items-start justify-between gap-4 min-w-[300px]`}
    >
      <div className="flex-1">
        <ToastPrimitive.Title className="font-semibold text-sm mb-1">{title}</ToastPrimitive.Title>
        {description && (
          <ToastPrimitive.Description className="text-sm opacity-90">{description}</ToastPrimitive.Description>
        )}
      </div>
      <ToastPrimitive.Close className="flex-shrink-0">
        <X className="w-4 h-4" />
      </ToastPrimitive.Close>
    </ToastPrimitive.Root>
  );
}

export function ToastContainer() {
  const { toasts } = useToast();
  return (
    <>
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} />
      ))}
    </>
  );
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <ToastPrimitive.Provider swipeDirection="right" duration={5000}>
      {children}
      <ToastPrimitive.Viewport className="fixed bottom-0 right-0 z-50 flex flex-col gap-2 p-6 w-full max-w-[420px] m-0" />
      <ToastContainer />
    </ToastPrimitive.Provider>
  );
}

