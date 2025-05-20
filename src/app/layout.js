'use client';

import '@/app/globals.css'
import { ThemeProvider } from "@/components/theme-provider"
import { NavHeader } from "@/components/nav-header"
import { permanentMarker, fZeroFont } from './fonts'
import { metadata } from './metadata' // Keep metadata import for potential use elsewhere, though not directly used in client component layout
import { Inter } from 'next/font/google'
import { ToastProvider } from '@/components/hooks/use-toast'
import { Toaster } from '@/components/ui/toaster'
import { FileUpIcon } from '@/components/icons'
import { usePathname } from 'next/navigation';
import { createClient } from '@/lib/supabase'
import { SessionContextProvider } from '@supabase/auth-helpers-react'

const inter = Inter({ subsets: ['latin'] })

// Export metadata if needed in other files, but it won't be used by the client layout itself
// export { metadata }

export default function RootLayout({ children }) {
  const pathname = usePathname();
  const pageName = pathname.split('/').filter(Boolean)[0] || 'home'; // Extract page name, default to 'home' for root
  const themeClass = `theme-${pageName}`;
  const supabase = createClient();

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${fZeroFont.variable} min-h-screen ${inter.className}`}>
        <SessionContextProvider supabaseClient={supabase}>
          <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
            <ToastProvider>
              <NavHeader />
              <main className={`container py-6 ${themeClass}`}>
                {children}
              </main>
              <Toaster />
            </ToastProvider>
          </ThemeProvider>
        </SessionContextProvider>
      </body>
    </html>
  );
}
