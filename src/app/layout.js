import '@/app/globals.css'
import { ThemeProvider } from "@/components/theme-provider"
import { permanentMarker, fZeroFont } from './fonts'
import { metadata } from './metadata'

export { metadata }

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${fZeroFont.variable}`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
