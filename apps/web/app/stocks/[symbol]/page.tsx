import { getStock, getStockHistory } from '@/lib/api';

type Props = { params: Promise<{ symbol: string }> };

export default async function StockDetailPage({ params }: Props) {
  const { symbol } = await params;
  const stock = await getStock(symbol);
  const history = await getStockHistory(symbol);

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-semibold">{stock?.symbol}</h1>
      <p className="mt-1 text-slate-400">{stock?.name} · {stock?.exchange} · {stock?.sector}</p>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-xs text-slate-400">Latest Close</p>
          <p className="mt-2 text-2xl font-semibold">{stock?.latest_close?.toFixed(2) ?? 'N/A'}</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-xs text-slate-400">Industry</p>
          <p className="mt-2 text-lg font-medium">{stock?.industry ?? 'N/A'}</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-xs text-slate-400">Latest Recommendation</p>
          <p className="mt-2 text-lg font-medium">{stock?.latest_recommendation?.action ?? 'N/A'}</p>
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-xl font-semibold">Recent Price History</h2>
        <div className="mt-4 overflow-hidden rounded-xl border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-slate-300">
              <tr>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-right">Open</th>
                <th className="px-4 py-3 text-right">High</th>
                <th className="px-4 py-3 text-right">Low</th>
                <th className="px-4 py-3 text-right">Close</th>
              </tr>
            </thead>
            <tbody>
              {history.slice(0, 15).map((row) => (
                <tr key={row.price_date} className="border-t border-slate-800">
                  <td className="px-4 py-3 text-slate-400">{row.price_date}</td>
                  <td className="px-4 py-3 text-right">{row.open?.toFixed(2) ?? '-'}</td>
                  <td className="px-4 py-3 text-right">{row.high?.toFixed(2) ?? '-'}</td>
                  <td className="px-4 py-3 text-right">{row.low?.toFixed(2) ?? '-'}</td>
                  <td className="px-4 py-3 text-right">{row.close?.toFixed(2) ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
