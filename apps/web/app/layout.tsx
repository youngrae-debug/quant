import './globals.css';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { SiteHeader } from '@/components/site-header';

const defaultSiteUrl =
  process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : 'https://www.wearethesecret.com';
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? defaultSiteUrl;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  applicationName: 'WATS',
  title: {
    default: 'We Are The Secret (WATS) | Systematic Equity Research',
    template: '%s | WATS',
  },
  description:
    'WATS is the We Are The Secret platform for explainable stock rankings and recommendations powered by point-in-time fundamentals, momentum, and expectation signals.',
  keywords: [
    'WATS',
    'We Are The Secret',
    'systematic equity research',
    'stock rankings',
    'quantitative investing',
  ],
  alternates: {
    canonical: '/',
  },
  openGraph: {
    siteName: 'WATS',
    title: 'We Are The Secret (WATS) | Systematic Equity Research',
    description:
      'The We Are The Secret platform for explainable stock rankings and recommendations powered by point-in-time data and transparent metrics.',
    type: 'website',
    url: '/',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'We Are The Secret (WATS)',
    description: 'Systematic equity research with transparent scoring and recommendation rationale.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-snippet': -1,
      'max-image-preview': 'large',
      'max-video-preview': -1,
    },
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-theme="dark">
      <body className="min-h-screen bg-black text-white antialiased">
        <SiteHeader />
        {children}
      </body>
    </html>
  );
}
