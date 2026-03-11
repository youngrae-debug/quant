import Link from 'next/link';
import { getTopPicks } from '@/lib/api';

type Props = {
  searchParams?: Promise<{ page?: string; size?: string }>;
};

export default async function TopPicksPage({ searchParams }: Props) {
  const params = (await searchParams) ?? {};
  const page = Math.max(1, Number(params.page ?? '1') || 1);
  const size = Math.min(100, Math.max(10, Number(params.size ?? '50') || 50));
  const data = await getTopPicks(page, size);
  const picks = data.items;
  const total = data.meta.total;
  const totalPages = Math.max(1, Math.ceil(total / size));
  const prevPage = Math.max(1, page - 1);
  const nextPage = Math.min(totalPages, page + 1);

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Top Picks</h1>
      <p className="mt-2 text-slate-400">Latest high-conviction signals from our model. Total: {total.toLocaleString()}</p>
      <div className="mt-8 grid gap-4">
        {picks.map((pick) => (
          <article key={`${pick.symbol}-${pick.recommendation_date}`} className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="flex items-center justify-between">
              <Link href={`/stocks/${pick.symbol}`} className="text-xl font-semibold text-emerald-300">{pick.symbol}</Link>
              <span className="rounded-full border border-emerald-500/30 px-3 py-1 text-xs uppercase text-emerald-300">{pick.action}</span>
            </div>
            <p className="mt-3 text-slate-300">{pick.rationale ?? 'No rationale provided.'}</p>
          </article>
        ))}
      </div>
      <div className="mt-8 flex items-center justify-between text-sm text-slate-300">
        <Link
          href={`/top-picks?page=${prevPage}&size=${size}`}
          className={`rounded border px-3 py-2 ${page <= 1 ? 'pointer-events-none border-slate-800 text-slate-600' : 'border-slate-700 hover:border-emerald-400'}`}
        >
          Previous
        </Link>
        <p>
          Page {page} / {totalPages}
        </p>
        <Link
          href={`/top-picks?page=${nextPage}&size=${size}`}
          className={`rounded border px-3 py-2 ${page >= totalPages ? 'pointer-events-none border-slate-800 text-slate-600' : 'border-slate-700 hover:border-emerald-400'}`}
        >
          Next
        </Link>
      </div>
    </main>
  );
}
