import Link from 'next/link';
import { getHealth } from '@/lib/api';

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main className="mx-auto max-w-6xl px-6 py-16">
      <section className="rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950 p-10">
        <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Systematic Equity Research</p>
        <h1 className="mt-4 text-5xl font-semibold tracking-tight">Institutional-grade insights, built for trust.</h1>
        <p className="mt-4 max-w-3xl text-slate-300">
          Quant combines point-in-time fundamentals, technical momentum, and expectation signals into transparent rankings and recommendations.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/top-picks" className="rounded-lg bg-emerald-400 px-5 py-2 text-sm font-medium text-slate-900">Explore Top Picks</Link>
          <Link href="/about-methodology" className="rounded-lg border border-slate-700 px-5 py-2 text-sm font-medium text-slate-200">Read Methodology</Link>
        </div>
        <p className="mt-8 text-sm text-slate-400">API health: <span className="font-medium text-slate-200">{health?.status ?? 'unavailable'}</span></p>
      </section>
    </main>
  );
}
