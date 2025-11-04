'use client';

import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';

interface DrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  children: React.ReactNode;
}

export default function Drawer({ open, onOpenChange, title, children }: DrawerProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-white shadow-layered z-50 flex flex-col">
          {title && (
            <div className="flex items-center justify-between p-6 border-b border-neutral-200">
              <Dialog.Title className="text-lg font-semibold">{title}</Dialog.Title>
              <Dialog.Close className="p-1 hover:bg-neutral-100 rounded-base transition-colors">
                <X className="w-5 h-5" />
              </Dialog.Close>
            </div>
          )}
          <div className="flex-1 overflow-y-auto p-6">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

