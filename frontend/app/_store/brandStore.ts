'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface BrandStore {
  selectedBrandId: string | null;
  setSelectedBrandId: (brandId: string | null) => void;
}

export const useBrandStore = create<BrandStore>()(
  persist(
    (set) => ({
      selectedBrandId: null,
      setSelectedBrandId: (brandId) => {
        set({ selectedBrandId: brandId });
        if (brandId) {
          localStorage.setItem('brandId', brandId);
        } else {
          localStorage.removeItem('brandId');
        }
      },
    }),
    {
      name: 'brand-storage',
    }
  )
);

