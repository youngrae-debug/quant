import Link from 'next/link';
import { getTopPicks } from '@/lib/api';

export default async function TopPicksPage() {
  const picks = await getTopPicks();

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Top Picks</h1>
      <p className="mt-2 text-slate-400">Latest high-conviction signals from our model.</p>
      <div className="mt-8 grid gap-4">
        {picks.map((pick) => (
          <article key={pick.symbol} className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between">
              <Link href={`/stocks/${pick.symbol}`} className="text-xl font-semibold text-emerald-300">{pick.symbol}</Link>
              <span className="rounded-full border border-emerald-500/30 px-3 py-1 text-xs uppercase text-emerald-300">{pick.action}</span>
            </div>
            <p className="mt-3 text-slate-300">{pick.rationale ?? 'No rationale provided.'}</p>
          </article>
        ))}
      </div>
    </main>
  );
}
