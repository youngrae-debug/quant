import Link from 'next/link';
import { getTurnarounds } from '@/lib/api';

type Props = {
  searchParams?: Promise<{ page?: string; size?: string }>;
};

function fmt(v: number): string {
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(v);
}

export default async function TurnaroundsPage({ searchParams }: Props) {
  const params = (await searchParams) ?? {};
  const page = Math.max(1, Number(params.page ?? '1') || 1);
  const size = Math.min(100, Math.max(10, Number(params.size ?? '50') || 50));
  const data = await getTurnarounds(page, size);
  const rows = data.items;
  const total = data.meta.total;
  const totalPages = Math.max(1, Math.ceil(total / size));
  const prevPage = Math.max(1, page - 1);
  const nextPage = Math.min(totalPages, page + 1);

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Turnaround Candidates</h1>
      <p className="mt-2 text-zinc-400">Companies shifting from losses to profitability within a two-year window. Total: {total.toLocaleString()}</p>

      <div className="mt-8 grid gap-4">
        {rows.map((row) => (
          <Link
            key={`${row.symbol}-${row.base_year}-${row.turnaround_year}`}
            href={`/stocks/${row.symbol}`}
            className="block rounded-xl border border-zinc-800 bg-zinc-950 p-5 transition hover:border-zinc-600"
          >
            <article>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xl font-semibold text-white">{row.symbol}</p>
                  <p className="mt-1 text-sm text-zinc-400">{row.name ?? '-'}</p>
                </div>
                <span className="rounded-full border border-zinc-700 px-3 py-1 text-xs uppercase text-zinc-300">
                  {row.base_year} → {row.next_year} → {row.turnaround_year}
                </span>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-zinc-800 bg-black p-3">
                  <p className="text-xs text-zinc-500">Base Year Net Income</p>
                  <p className="mt-1 text-lg font-medium text-rose-300">{fmt(row.base_year_net_income)}</p>
                </div>
                <div className="rounded-lg border border-zinc-800 bg-black p-3">
                  <p className="text-xs text-zinc-500">Turnaround Year Net Income</p>
                  <p className="mt-1 text-lg font-medium text-white">{fmt(row.turnaround_year_net_income)}</p>
                </div>
              </div>
            </article>
          </Link>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-between text-sm text-zinc-300">
        <Link href={`/turnarounds?page=${prevPage}&size=${size}`} className={`rounded border px-3 py-2 ${page <= 1 ? 'pointer-events-none border-zinc-800 text-zinc-500' : 'border-zinc-700 hover:border-zinc-600'}`}>
          Previous
        </Link>
        <p>Page {page} / {totalPages}</p>
        <Link href={`/turnarounds?page=${nextPage}&size=${size}`} className={`rounded border px-3 py-2 ${page >= totalPages ? 'pointer-events-none border-zinc-800 text-zinc-500' : 'border-zinc-700 hover:border-zinc-600'}`}>
          Next
        </Link>
      </div>
    </main>
  );
}
