'use client';

import { useState } from 'react';
import TopNav from './TopNav';
import LeftNav from './LeftNav';
import RightPanel from './RightPanel';

interface LayoutShellProps {
  children: React.ReactNode;
  pageTitle?: string;
  pageSubtitle?: string;
  rightPanelContent?: React.ReactNode;
}

export default function LayoutShell({
  children,
  pageTitle,
  pageSubtitle,
  rightPanelContent,
}: LayoutShellProps) {
  const [rightPanelOpen, setRightPanelOpen] = useState(true);

  return (
    <div className="min-h-screen bg-neutral-50">
      <TopNav />
      <div className="flex">
        <LeftNav />
        <main className="flex-1 ml-64">
          <div className="flex">
            <div className="flex-1 p-8">
              {(pageTitle || pageSubtitle) && (
                <div className="mb-6">
                  {pageTitle && (
                    <h1 className="text-3xl font-semibold text-neutral-900 mb-2">
                      {pageTitle}
                    </h1>
                  )}
                  {pageSubtitle && (
                    <p className="text-base text-neutral-600">{pageSubtitle}</p>
                  )}
                </div>
              )}
              {children}
            </div>
            {rightPanelOpen && rightPanelContent && (
              <RightPanel onClose={() => setRightPanelOpen(false)}>
                {rightPanelContent}
              </RightPanel>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

