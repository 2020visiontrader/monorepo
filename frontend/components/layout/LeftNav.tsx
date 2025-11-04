'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import {
  LayoutDashboard,
  UserPlus,
  Eye,
  Building2,
  FileText,
  Search,
  BookOpen,
  Palette,
  Settings,
  ListTodo,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navGroups = [
  {
    label: 'Overview',
    items: [
      { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    ],
  },
  {
    label: 'Setup',
    items: [
      { href: '/onboarding', label: 'Onboarding', icon: UserPlus },
      { href: '/competitors', label: 'Competitor Insights', icon: Eye },
    ],
  },
  {
    label: 'Content',
    items: [
      { href: '/build-site', label: 'Build My Site', icon: Building2 },
      { href: '/pdp-copy', label: 'PDP Copy', icon: FileText },
      { href: '/seo', label: 'SEO Optimize', icon: Search },
    ],
  },
  {
    label: 'Library',
    items: [
      { href: '/frameworks', label: 'Frameworks', icon: BookOpen },
      { href: '/templates', label: 'Store Templates', icon: Palette },
    ],
  },
  {
    label: 'System',
    items: [
      { href: '/jobs', label: 'Jobs', icon: ListTodo },
      { href: '/settings', label: 'Settings', icon: Settings },
    ],
  },
];

export default function LeftNav() {
  const pathname = usePathname();
  const [openGroups, setOpenGroups] = useState<Set<string>>(new Set(navGroups.map((g) => g.label)));

  const toggleGroup = (label: string) => {
    const newOpen = new Set(openGroups);
    if (newOpen.has(label)) {
      newOpen.delete(label);
    } else {
      newOpen.add(label);
    }
    setOpenGroups(newOpen);
  };

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-neutral-200 overflow-y-auto">
      <nav className="p-4 space-y-1">
        {navGroups.map((group) => {
          const isOpen = openGroups.has(group.label);
          const hasActiveItem = group.items.some(
            (item) => pathname === item.href || pathname?.startsWith(`${item.href}/`)
          );

          return (
            <div key={group.label}>
              <button
                onClick={() => toggleGroup(group.label)}
                className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-neutral-500 uppercase tracking-wider hover:bg-neutral-50 rounded-base transition-colors"
              >
                <span>{group.label}</span>
                {isOpen ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>
              {isOpen && (
                <div className="space-y-1 ml-2">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);

                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2 rounded-base transition-colors duration-fast',
                          isActive
                            ? 'bg-primary-50 text-primary-700 font-medium'
                            : 'text-neutral-700 hover:bg-neutral-100'
                        )}
                      >
                        <Icon className="w-5 h-5" />
                        <span>{item.label}</span>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}

