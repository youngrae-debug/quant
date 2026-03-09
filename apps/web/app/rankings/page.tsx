import Link from 'next/link';
import { getRankings } from '@/lib/api';

export default async function RankingsPage() {
  const rows = await getRankings();

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Rankings</h1>
      <div className="mt-6 overflow-hidden rounded-xl border border-slate-800">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-slate-300">
            <tr>
              <th className="px-4 py-3 text-left">Symbol</th>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-right">Final Score</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.symbol}-${row.score_date}`} className="border-t border-slate-800">
                <td className="px-4 py-3"><Link className="text-emerald-300" href={`/stocks/${row.symbol}`}>{row.symbol}</Link></td>
                <td className="px-4 py-3 text-slate-400">{row.score_date}</td>
                <td className="px-4 py-3 text-right font-medium">{row.final_score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
