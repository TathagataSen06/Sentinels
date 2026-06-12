import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';
import { Providers } from '@/components/Providers';

export const metadata: Metadata = {
  title: 'Sentinels SOC Platform',
  description: 'Enterprise Security Operations Center Dashboard — Real-time threat detection, MITRE ATT&CK mapping, and incident response.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-gray-950 text-white min-h-screen flex overflow-hidden">
        <Providers>
          <Sidebar />
          <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <div className="flex-1 overflow-y-auto p-8">
              {children}
            </div>
          </main>
        </Providers>
      </body>
    </html>
  );
}
