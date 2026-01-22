'use client';

import './globals.css'
import { outfit, jetbrainsMono } from './fonts'
import { Toaster } from '@/components/ui/sonner'
import { ThemeProvider } from 'next-themes'
import { usePathname } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

export default function RootLayout({ children }) {
  const pathname = usePathname();
  const pageName = pathname.split('/').filter(Boolean)[0] || 'home';
  const themeClass = `theme-${pageName}`;

  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning className={`${outfit.variable} ${jetbrainsMono.variable} font-sans min-h-screen bg-background text-foreground antialiased selection:bg-primary/30 overflow-hidden`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false} disableTransitionOnChange>
          <div className="relative flex h-screen w-full overflow-hidden bg-background">
              {/* Fixed Sidebar */}
              <Sidebar />

              {/* Main Content Area */}
              <div className="flex flex-1 flex-col overflow-hidden">
                  <Header />
                  <main className={`flex-1 overflow-auto p-6 ${themeClass}`}>
                      <div className="mx-auto max-w-7xl animate-fadeIn">
                           {children}
                      </div>
                  </main>
              </div>
          </div>
          <Toaster position="top-right" richColors closeButton />
        </ThemeProvider>
      </body>
    </html>
  );
}
