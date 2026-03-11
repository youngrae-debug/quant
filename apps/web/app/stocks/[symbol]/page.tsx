import { getStock, getStockHistory } from '@/lib/api';

type Props = { params: Promise<{ symbol: string }> };

function safePercentChange(current: number | null | undefined, previous: number | null | undefined): string {
  if (current == null || previous == null || previous === 0) return 'N/A';
  const pct = ((current - previous) / previous) * 100;
  const sign = pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
}

function getMomentumBadge(close: number | null | undefined, previousClose: number | null | undefined): {
  label: string;
  className: string;
} {
  if (close == null || previousClose == null) {
    return { label: 'Insufficient data', className: 'border-slate-700 text-slate-300' };
  }

  if (close > previousClose) {
    return { label: 'Positive momentum', className: 'border-emerald-500/40 text-emerald-300' };
  }

  if (close < previousClose) {
    return { label: 'Negative momentum', className: 'border-rose-500/40 text-rose-300' };
  }

  return { label: 'Neutral momentum', className: 'border-slate-700 text-slate-300' };
}

export default async function StockDetailPage({ params }: Props) {
  const { symbol } = await params;
  const stock = await getStock(symbol);
  const history = await getStockHistory(symbol);

  const latest = history[0] ?? null;
  const prev = history[1] ?? null;
  const closeDelta = safePercentChange(latest?.close, prev?.close);
  const weekAnchor = history[Math.min(5, Math.max(0, history.length - 1))] ?? null;
  const weekDelta = safePercentChange(latest?.close, weekAnchor?.close);
  const momentumBadge = getMomentumBadge(latest?.close, prev?.close);

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

      <section className="mt-10 rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h2 className="text-xl font-semibold">Financial Data Snapshot</h2>
        <p className="mt-2 text-sm text-slate-400">
          Company-level snapshot from the latest available market and profile data.
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">Ticker</p>
            <p className="mt-1 font-medium">{stock?.symbol ?? 'N/A'}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">Exchange</p>
            <p className="mt-1 font-medium">{stock?.exchange ?? 'N/A'}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">Sector / Industry</p>
            <p className="mt-1 font-medium">{stock?.sector ?? 'N/A'} / {stock?.industry ?? 'N/A'}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">Latest Price Date</p>
            <p className="mt-1 font-medium">{stock?.latest_price_date ?? 'N/A'}</p>
          </div>
        </div>
      </section>

      <section className="mt-6 rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h2 className="text-xl font-semibold">Institutional Ownership Signals</h2>
        <p className="mt-2 text-sm text-slate-400">
          Ownership-feed integration can be layered here (13F/holder concentration/net accumulation). For now, we surface market-behavior proxies until holdings ingestion is enabled.
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">1D Close Change</p>
            <p className="mt-1 text-lg font-medium">{closeDelta}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">~1W Close Change</p>
            <p className="mt-1 text-lg font-medium">{weekDelta}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
            <p className="text-xs text-slate-400">Signal State</p>
            <span className={`mt-1 inline-flex rounded-full border px-2 py-1 text-xs ${momentumBadge.className}`}>
              {momentumBadge.label}
            </span>
          </div>
        </div>
      </section>

      <section className="mt-6 rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h2 className="text-xl font-semibold">Metrics Engine View</h2>
        <p className="mt-2 text-sm text-slate-400">
          Quick interpretation panel combining recommendation, price behavior, and data freshness into a transparent per-symbol summary.
        </p>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-300">
          <li>Current action: <span className="font-medium text-white">{stock?.latest_recommendation?.action ?? 'N/A'}</span></li>
          <li>Recommendation date: <span className="font-medium text-white">{stock?.latest_recommendation?.recommendation_date ?? 'N/A'}</span></li>
          <li>Conviction: <span className="font-medium text-white">{stock?.latest_recommendation?.conviction != null ? stock.latest_recommendation.conviction.toFixed(2) : 'N/A'}</span></li>
          <li>Most recent close trend: <span className="font-medium text-white">{momentumBadge.label}</span></li>
        </ul>
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
