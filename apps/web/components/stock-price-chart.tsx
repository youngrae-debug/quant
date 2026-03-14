'use client';

import { useMemo, useState } from 'react';
import type { PriceHistoryItem } from '@/lib/api';

type Props = {
  history: PriceHistoryItem[];
};

const ranges = [
  { label: '1M', days: 30 },
  { label: '3M', days: 90 },
  { label: '6M', days: 180 },
  { label: '1Y', days: 365 },
  { label: 'MAX', days: 9999 },
] as const;

export function StockPriceChart({ history }: Props) {
  const [days, setDays] = useState<number>(180);

  const chartData = useMemo(() => {
    const filtered = history
      .slice()
      .reverse()
      .filter((item) => item.close != null)
      .slice(-days);

    if (filtered.length === 0) return { points: '', min: 0, max: 0, latest: null as number | null };

    const closes = filtered.map((item) => Number(item.close));
    const min = Math.min(...closes);
    const max = Math.max(...closes);
    const latest = closes[closes.length - 1] ?? null;
    const spread = max - min || 1;

    const points = filtered
      .map((item, idx) => {
        const x = (idx / Math.max(1, filtered.length - 1)) * 100;
        const y = 100 - ((Number(item.close) - min) / spread) * 100;
        return `${x},${y}`;
      })
      .join(' ');

    return { points, min, max, latest };
  }, [days, history]);

  return (
    <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">Price Trend Chart</h2>
          <p className="mt-1 text-sm text-zinc-400">
            Latest close: {chartData.latest != null ? chartData.latest.toFixed(2) : 'N/A'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {ranges.map((range) => (
            <button
              key={range.label}
              type="button"
              onClick={() => setDays(range.days)}
              className={`rounded border px-2.5 py-1 text-xs transition ${days === range.days ? 'border-white text-white' : 'border-zinc-700 text-zinc-400 hover:border-zinc-500'}`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-zinc-800 bg-black p-3">
        {chartData.points ? (
          <>
            <svg viewBox="0 0 100 100" className="h-52 w-full">
              <polyline
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="text-white"
                points={chartData.points}
                vectorEffect="non-scaling-stroke"
              />
            </svg>
            <div className="mt-2 flex justify-between text-xs text-zinc-500">
              <span>Low {chartData.min.toFixed(2)}</span>
              <span>High {chartData.max.toFixed(2)}</span>
            </div>
          </>
        ) : (
          <p className="text-sm text-zinc-400">No chart data available.</p>
        )}
      </div>
    </section>
  );
}
