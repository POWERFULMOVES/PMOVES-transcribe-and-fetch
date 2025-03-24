import '@/app/globals.css'
import { ThemeProvider } from "@/components/theme-provider"
import { NavHeader } from "@/components/nav-header"
import { permanentMarker, fZeroFont } from './fonts'
import { metadata } from './metadata'
import { Inter } from 'next/font/google'
import { ToastProvider } from '@/components/hooks/use-toast'
import { Toaster } from '@/components/ui/toaster'
import { FileUpIcon } from '@/components/icons'

const inter = Inter({ subsets: ['latin'] })

export { metadata }

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${fZeroFont.variable} min-h-screen ${inter.className}`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <ToastProvider>
            <NavHeader />
            <main className="container py-6">
              {children}
            </main>
            <Toaster />
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
