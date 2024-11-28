import '@/app/globals.css'
import { ThemeProvider } from "@/components/theme-provider"
import { NavHeader } from "@/components/nav-header"
import { permanentMarker, fZeroFont } from './fonts'
import { metadata } from './metadata'

export { metadata }

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${fZeroFont.variable} min-h-screen`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <NavHeader />
          <main className="container py-6">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}
