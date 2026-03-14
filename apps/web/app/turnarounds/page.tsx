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
      <p className="mt-2 text-zinc-400">Companies shifting from loss this year to profitability in two years. Total: {total.toLocaleString()}</p>

      <div className="mt-6 overflow-hidden rounded-xl border border-zinc-800">
        <table className="w-full text-sm">
          <thead className="bg-zinc-950 text-zinc-300">
            <tr>
              <th className="px-4 py-3 text-left">Symbol</th>
              <th className="px-4 py-3 text-left">Company</th>
              <th className="px-4 py-3 text-right">Base Year NI</th>
              <th className="px-4 py-3 text-right">Turnaround Year NI</th>
              <th className="px-4 py-3 text-left">Window</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.symbol}-${row.base_year}-${row.turnaround_year}`} className="border-t border-zinc-800">
                <td className="px-4 py-3"><Link className="text-white" href={`/stocks/${row.symbol}`}>{row.symbol}</Link></td>
                <td className="px-4 py-3 text-zinc-300">{row.name ?? '-'}</td>
                <td className="px-4 py-3 text-right text-rose-300">{fmt(row.base_year_net_income)}</td>
                <td className="px-4 py-3 text-right text-white">{fmt(row.turnaround_year_net_income)}</td>
                <td className="px-4 py-3 text-zinc-400">{row.base_year} → {row.next_year} → {row.turnaround_year}</td>
              </tr>
            ))}
          </tbody>
        </table>
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
