import type { Metadata, Viewport } from 'next';
import './globals.css';
import Header from '@/components/ui/Header';
import BottomNav from '@/components/ui/BottomNav';

export const metadata: Metadata = {
  title: 'alisha bubbzieee',
  description: 'Private conversational reconstruction engine for Alisha',
  manifest: '/manifest.json',
  icons: {
    icon: '/icons/icon-192.svg',
    apple: '/icons/icon-192.svg',
  },
};

export const viewport: Viewport = {
  themeColor: '#111210',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400;1,700&family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Noto+Naskh+Arabic:wght@400;600;700&family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[var(--theme-bg,#0A0B09)] text-ivory font-sans antialiased h-screen h-[100dvh] w-screen overflow-hidden select-none transition-colors duration-300">
        <div className="w-full h-full bg-deep flex flex-col relative overflow-hidden transition-colors duration-300">
          <Header />
          <main className="flex-1 relative overflow-hidden flex flex-col w-full">
            {children}
          </main>
          <BottomNav />
        </div>
      </body>
    </html>
  );
}
