'use client';

import { useState, useEffect, useCallback } from 'react';

interface ToastState {
  id: string;
  title: string;
  description?: string;
  variant: 'success' | 'error' | 'info';
}

let toastState: ToastState[] = [];
let listeners: Array<() => void> = [];

const notify = () => {
  listeners.forEach((listener) => listener());
};

export const toast = {
  success: (title: string, description?: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    toastState.push({
      id,
      title,
      description,
      variant: 'success',
    });
    notify();
    // Auto-remove after 5 seconds
    setTimeout(() => {
      toastState = toastState.filter((t) => t.id !== id);
      notify();
    }, 5000);
  },
  error: (title: string, description?: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    toastState.push({
      id,
      title,
      description,
      variant: 'error',
    });
    notify();
    setTimeout(() => {
      toastState = toastState.filter((t) => t.id !== id);
      notify();
    }, 7000);
  },
  info: (title: string, description?: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    toastState.push({
      id,
      title,
      description,
      variant: 'info',
    });
    notify();
    setTimeout(() => {
      toastState = toastState.filter((t) => t.id !== id);
      notify();
    }, 5000);
  },
};

export function useToast() {
  const [, setState] = useState(0);

  useEffect(() => {
    const update = () => {
      setState((prev) => prev + 1);
    };
    listeners.push(update);
    return () => {
      listeners = listeners.filter((l) => l !== update);
    };
  }, []);

  const remove = useCallback((id: string) => {
    toastState = toastState.filter((t) => t.id !== id);
    notify();
  }, []);

  return { toasts: toastState, remove };
}

export { ToastProvider } from '@/components/primitives/Toast';

