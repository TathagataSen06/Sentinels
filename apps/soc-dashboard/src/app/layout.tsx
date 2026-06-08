import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';
import { Providers } from '@/components/Providers';

export const metadata: Metadata = {
  title: 'Sentinels SOC Platform',
  description: 'Enterprise Security Operations Center Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-950 text-white min-h-screen flex">
        <Providers>
          <Sidebar />
          <main className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-8">
              {children}
            </div>
          </main>
        </Providers>
      </body>
    </html>
  );
}
