import './globals.css';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { SiteHeader } from '@/components/site-header';

const defaultSiteUrl =
  process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : 'https://www.wearethesecret.com';
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? defaultSiteUrl;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'WATS | Systematic Equity Research',
    template: '%s | WATS',
  },
  description:
    'WATS provides explainable stock rankings and recommendations powered by point-in-time fundamentals, momentum, and expectation signals.',
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'WATS',
    description:
      'Explainable stock rankings and recommendations powered by point-in-time data and transparent metrics.',
    type: 'website',
    url: '/',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'WATS',
    description: 'Systematic equity research with transparent scoring and recommendation rationale.',
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-theme="light">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <SiteHeader />
        {children}
      </body>
    </html>
  );
}
