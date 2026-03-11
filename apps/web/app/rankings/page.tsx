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
      <p className="mt-2 text-slate-400">Latest ranked universe. Total: {total.toLocaleString()}</p>

      <form className="mt-6 flex gap-3" action="/rankings" method="get">
        <input type="hidden" name="size" value={size} />
        <input
          name="q"
          defaultValue={q}
          placeholder="Search by ticker or company"
          className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder:text-slate-500"
        />
        <button className="rounded border border-emerald-400 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-400/10">Search</button>
      </form>

      <div className="mt-6 overflow-hidden rounded-xl border border-slate-800">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-slate-300">
            <tr>
              <th className="px-4 py-3 text-left">Symbol</th>
              <th className="px-4 py-3 text-left">Company</th>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-right">Final Score</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.symbol}-${row.score_date}`} className="border-t border-slate-800">
                <td className="px-4 py-3"><Link className="text-emerald-300" href={`/stocks/${row.symbol}`}>{row.symbol}</Link></td>
                <td className="px-4 py-3 text-slate-400">{row.name ?? '-'}</td>
                <td className="px-4 py-3 text-slate-400">{row.score_date}</td>
                <td className="px-4 py-3 text-right font-medium">{row.final_score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-8 flex items-center justify-between text-sm text-slate-300">
        <Link
          href={`/rankings?page=${prevPage}&size=${size}${qs}`}
          className={`rounded border px-3 py-2 ${page <= 1 ? 'pointer-events-none border-slate-800 text-slate-600' : 'border-slate-700 hover:border-emerald-400'}`}
        >
          Previous
        </Link>
        <p>
          Page {page} / {totalPages}
        </p>
        <Link
          href={`/rankings?page=${nextPage}&size=${size}${qs}`}
          className={`rounded border px-3 py-2 ${page >= totalPages ? 'pointer-events-none border-slate-800 text-slate-600' : 'border-slate-700 hover:border-emerald-400'}`}
        >
          Next
        </Link>
      </div>
    </main>
  );
}
