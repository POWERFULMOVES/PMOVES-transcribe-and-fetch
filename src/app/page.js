"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import DashboardView from '@/components/views/DashboardView';

export default function Home() {
  const router = useRouter();

  const handleViewChange = (view) => {
    switch (view) {
      case 'transcribe':
        router.push('/transcribe');
        break;
      case 'fetch':
        router.push('/fetch');
        break;
      case 'search':
        router.push('/vector-search');
        break;
      default:
        console.warn(`Unknown view: ${view}`);
    }
  };

  return (
    <main className="min-h-screen bg-[hsl(var(--background))]">
      <DashboardView onViewChange={handleViewChange} />
    </main>
  );
}
