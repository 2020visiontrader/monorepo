'use client';

import { Search, HelpCircle, User, ChevronDown, Building2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { usePathname } from 'next/navigation';
import { useBrandStore } from '@/app/_store/brandStore';
import api from '@/lib/api';

export default function TopNav() {
  const environment = process.env.NEXT_PUBLIC_ENV || 'ST';
  const pathname = usePathname();
  const [brandOpen, setBrandOpen] = useState(false);
  const { selectedBrandId, setSelectedBrandId } = useBrandStore();
  const [brands, setBrands] = useState<any[]>([]);
  const [currentBrand, setCurrentBrand] = useState<{ name: string; logo: string | null; id: string } | null>(null);
  const [currentOrg, setCurrentOrg] = useState<{ name: string } | null>(null);

  useEffect(() => {
    // Fetch brands
    api.get('/brands/')
      .then((res) => {
        setBrands(res.data.results || res.data || []);
        if (selectedBrandId) {
          const brand = (res.data.results || res.data || []).find((b: any) => b.id === selectedBrandId);
          if (brand) {
            setCurrentBrand({ name: brand.name, logo: null, id: brand.id });
          }
        } else if (res.data.results?.length > 0 || res.data?.length > 0) {
          const firstBrand = res.data.results?.[0] || res.data[0];
          setSelectedBrandId(firstBrand.id);
          setCurrentBrand({ name: firstBrand.name, logo: null, id: firstBrand.id });
        }
      })
      .catch(() => {
        // Fallback to mock data
        setBrands([
          { id: '1', name: 'Demo Brand A' },
          { id: '2', name: 'Demo Brand B' },
        ]);
        if (!selectedBrandId) {
          setSelectedBrandId('1');
          setCurrentBrand({ name: 'Demo Brand A', logo: null, id: '1' });
        }
      });
    
    // Fetch org info
    api.get('/auth/me')
      .then((res) => {
        if (res.data.orgs?.length > 0) {
          setCurrentOrg({ name: res.data.orgs[0].name });
        }
      })
      .catch(() => {
        setCurrentOrg({ name: 'Demo Organization' });
      });
  }, [selectedBrandId, setSelectedBrandId]);

  // Generate breadcrumbs from pathname
  const pathSegments = pathname?.split('/').filter(Boolean) || [];
  const breadcrumbs = pathSegments.map((segment, index) => ({
    label: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
    path: '/' + pathSegments.slice(0, index + 1).join('/'),
  }));

  return (
    <nav className="h-16 border-b border-neutral-200 bg-white flex items-center justify-between px-6">
      <div className="flex items-center gap-4 flex-1">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-base flex items-center justify-center text-white font-bold">
            EO
          </div>
          <span className="font-semibold text-lg">E-Commerce Optimizer</span>
        </div>

        {/* Brand/Org Switcher */}
        {currentBrand && (
          <DropdownMenu.Root open={brandOpen} onOpenChange={setBrandOpen}>
            <DropdownMenu.Trigger asChild>
              <button className="flex items-center gap-2 px-3 py-1.5 hover:bg-neutral-100 rounded-base transition-colors">
                {currentBrand.logo ? (
                  <img src={currentBrand.logo} alt={currentBrand.name} className="w-6 h-6 rounded" />
                ) : (
                  <div className="w-6 h-6 bg-primary-100 rounded flex items-center justify-center">
                    <Building2 className="w-4 h-4 text-primary-700" />
                  </div>
                )}
                <span className="text-sm font-medium text-neutral-700">{currentBrand.name}</span>
                <ChevronDown className="w-4 h-4 text-neutral-500" />
              </button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
              <DropdownMenu.Content className="bg-white rounded-base shadow-layered border border-neutral-200 p-1 min-w-[200px]">
                {currentOrg && (
                  <>
                    <DropdownMenu.Label className="px-3 py-2 text-xs font-semibold text-neutral-500">
                      Organization: {currentOrg.name}
                    </DropdownMenu.Label>
                    <DropdownMenu.Separator className="h-px bg-neutral-200 my-1" />
                  </>
                )}
                {brands.map((brand) => (
                  <DropdownMenu.Item
                    key={brand.id}
                    onClick={() => {
                      setSelectedBrandId(brand.id);
                      setCurrentBrand({ name: brand.name, logo: null, id: brand.id });
                      setBrandOpen(false);
                      // Reload page data
                      window.location.reload();
                    }}
                    className={`px-3 py-2 text-sm hover:bg-neutral-100 rounded-base cursor-pointer ${
                      selectedBrandId === brand.id ? 'bg-primary-50 text-primary-700' : ''
                    }`}
                  >
                    {brand.name}
                  </DropdownMenu.Item>
                ))}
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        )}

        {/* Breadcrumb */}
        {breadcrumbs.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-neutral-600">
            {breadcrumbs.map((crumb, index) => (
              <span key={crumb.path} className="flex items-center gap-2">
                {index > 0 && <span>/</span>}
                <span className={index === breadcrumbs.length - 1 ? 'text-neutral-900 font-medium' : ''}>
                  {crumb.label}
                </span>
              </span>
            ))}
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4">
        <span className="px-2 py-1 text-xs font-medium bg-neutral-100 text-neutral-700 rounded">
          {environment}
        </span>
        <button className="p-2 hover:bg-neutral-100 rounded-base transition-colors">
          <Search className="w-5 h-5 text-neutral-600" />
        </button>
        <button className="p-2 hover:bg-neutral-100 rounded-base transition-colors">
          <HelpCircle className="w-5 h-5 text-neutral-600" />
        </button>
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="p-2 hover:bg-neutral-100 rounded-base transition-colors">
              <User className="w-5 h-5 text-neutral-600" />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content className="bg-white rounded-base shadow-layered border border-neutral-200 p-1 min-w-[180px]">
              <DropdownMenu.Item className="px-3 py-2 text-sm hover:bg-neutral-100 rounded-base cursor-pointer">
                Profile
              </DropdownMenu.Item>
              <DropdownMenu.Item className="px-3 py-2 text-sm hover:bg-neutral-100 rounded-base cursor-pointer">
                Settings
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="h-px bg-neutral-200 my-1" />
              <DropdownMenu.Item className="px-3 py-2 text-sm hover:bg-neutral-100 rounded-base cursor-pointer">
                Sign out
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>
    </nav>
  );
}

