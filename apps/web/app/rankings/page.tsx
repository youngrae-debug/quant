import Link from 'next/link';
import { getRankings } from '@/lib/api';

type Props = {
  searchParams?: Promise<{ page?: string; size?: string; q?: string }>;
};

export default async function RankingsPage({ searchParams }: Props) {
  const params = (await searchParams) ?? {};
  const page = Math.max(1, Number(params.page ?? '1') || 1);
  const size = Math.min(100, Math.max(10, Number(params.size ?? '50') || 50));
  const q = params.q?.trim() ?? '';
  const data = await getRankings(page, size, q);
  const rows = data.items;
  const total = data.meta.total;
  const totalPages = Math.max(1, Math.ceil(total / size));
  const prevPage = Math.max(1, page - 1);
  const nextPage = Math.min(totalPages, page + 1);
  const qs = q ? `&q=${encodeURIComponent(q)}` : '';

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Rankings</h1>
      <p className="mt-2 text-zinc-400">Latest ranked universe. Total: {total.toLocaleString()}</p>

      <form className="mt-6 flex gap-3" action="/rankings" method="get">
        <input type="hidden" name="size" value={size} />
        <input
          name="q"
          defaultValue={q}
          placeholder="Search by ticker or company"
          className="w-full rounded border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white placeholder:text-zinc-500"
        />
        <button className="rounded border border-zinc-600 px-4 py-2 text-sm text-white hover:bg-zinc-900">Search</button>
      </form>

      <div className="mt-8 grid gap-4">
        {rows.map((row) => (
          <Link
            key={`${row.symbol}-${row.score_date}`}
            href={`/stocks/${row.symbol}`}
            className="block rounded-xl border border-zinc-800 bg-zinc-950 p-5 transition hover:border-zinc-600"
          >
            <article>
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xl font-semibold text-white">{row.symbol}</p>
                  <p className="mt-1 text-sm text-zinc-400">{row.name ?? '-'}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs uppercase tracking-[0.14em] text-zinc-500">Final Score</p>
                  <p className="mt-1 text-xl font-semibold text-white">{row.final_score.toFixed(2)}</p>
                </div>
              </div>
              <p className="mt-3 text-sm text-zinc-400">Score Date: {row.score_date}</p>
            </article>
          </Link>
        ))}
      </div>
      <div className="mt-8 flex items-center justify-between text-sm text-zinc-300">
        <Link
          href={`/rankings?page=${prevPage}&size=${size}${qs}`}
          className={`rounded border px-3 py-2 ${page <= 1 ? 'pointer-events-none border-zinc-800 text-zinc-500' : 'border-zinc-700 hover:border-zinc-600'}`}
        >
          Previous
        </Link>
        <p>
          Page {page} / {totalPages}
        </p>
        <Link
          href={`/rankings?page=${nextPage}&size=${size}${qs}`}
          className={`rounded border px-3 py-2 ${page >= totalPages ? 'pointer-events-none border-zinc-800 text-zinc-500' : 'border-zinc-700 hover:border-zinc-600'}`}
        >
          Next
        </Link>
      </div>
    </main>
  );
}
