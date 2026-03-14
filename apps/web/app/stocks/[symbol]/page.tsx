import type { Metadata } from 'next';

import { getStock, getStockHistory } from '@/lib/api';
import { StockPriceChart } from '@/components/stock-price-chart';
import { StockDetailTabs } from '@/components/stock-detail-tabs';

type Props = { params: Promise<{ symbol: string }> };

type DcfScenario = {
  growth: number;
  discount: number;
  impliedPrice: number;
  upside: number | null;
};

function safePercentChange(current: number | null | undefined, previous: number | null | undefined): string {
  if (current == null || previous == null || previous === 0) return 'N/A';
  const pct = ((current - previous) / previous) * 100;
  const sign = pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
}



function buildDcfSensitivity(latestClose: number | null | undefined): DcfScenario[] {
  if (latestClose == null || latestClose <= 0) return [];

  const growthRates = [-0.02, 0.03, 0.08];
  const discountRates = [0.08, 0.1, 0.12];

  const scenarios: DcfScenario[] = [];
  for (const growth of growthRates) {
    for (const discount of discountRates) {
      const proxyCashflow = latestClose * 0.02;
      let pv = 0;
      for (let year = 1; year <= 5; year += 1) {
        const cf = proxyCashflow * (1 + growth) ** year;
        pv += cf / (1 + discount) ** year;
      }
      const terminalValue = (proxyCashflow * (1 + growth) ** 5 * 10) / (1 + discount) ** 5;
      const impliedPrice = Number((pv + terminalValue).toFixed(2));
      const upside = latestClose > 0 ? Number((((impliedPrice - latestClose) / latestClose) * 100).toFixed(2)) : null;

      scenarios.push({ growth, discount, impliedPrice, upside });
    }
  }

  return scenarios.sort((a, b) => b.impliedPrice - a.impliedPrice);
}

function getMomentumBadge(close: number | null | undefined, previousClose: number | null | undefined): {
  label: string;
  className: string;
} {
  if (close == null || previousClose == null) {
    return { label: 'Insufficient data', className: 'border-zinc-700 text-zinc-300' };
  }

  if (close > previousClose) {
    return { label: 'Positive momentum', className: 'border-zinc-600 text-white' };
  }

  if (close < previousClose) {
    return { label: 'Negative momentum', className: 'border-rose-500/40 text-rose-300' };
  }

  return { label: 'Neutral momentum', className: 'border-zinc-700 text-zinc-300' };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { symbol } = await params;
  const ticker = symbol.toUpperCase();
  const stock = await getStock(ticker);
  const title = stock?.name ? `${stock.name} (${ticker}) Stock Analysis | Quant` : `${ticker} Stock Analysis | Quant`;
  const description = stock?.latest_recommendation?.action
    ? `${ticker} detailed snapshot with financial profile, ownership signals, and metrics engine view. Latest model action: ${stock.latest_recommendation.action}.`
    : `${ticker} detailed snapshot with financial profile, ownership signals, and metrics engine view.`;

  return {
    title,
    description,
    alternates: {
      canonical: `/stocks/${ticker}`,
    },
    openGraph: {
      title,
      description,
      type: 'article',
      url: `/stocks/${ticker}`,
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}

export default async function StockDetailPage({ params }: Props) {
  const { symbol } = await params;
  const stock = await getStock(symbol);
  const history = await getStockHistory(symbol, 365);

  const latest = history[0] ?? null;
  const prev = history[1] ?? null;
  const closeDelta = safePercentChange(latest?.close, prev?.close);
  const weekAnchor = history[Math.min(5, Math.max(0, history.length - 1))] ?? null;
  const weekDelta = safePercentChange(latest?.close, weekAnchor?.close);
  const momentumBadge = getMomentumBadge(latest?.close, prev?.close);
  const dcfScenarios = buildDcfSensitivity(stock?.latest_close);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FinancialService',
    name: `${stock?.symbol ?? symbol.toUpperCase()} Stock Detail`,
    description: 'Financial snapshot, ownership signal proxy, and metrics engine summary for an individual stock.',
    provider: {
      '@type': 'Organization',
      name: 'Quant',
    },
    areaServed: 'Global',
  };

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <h1 className="text-3xl font-semibold">{stock?.symbol}</h1>
      <p className="mt-1 text-zinc-400">{stock?.name} · {stock?.exchange} · {stock?.sector}</p>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <p className="text-xs text-zinc-400">Latest Close</p>
          <p className="mt-2 text-2xl font-semibold">{stock?.latest_close?.toFixed(2) ?? 'N/A'}</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <p className="text-xs text-zinc-400">Industry</p>
          <p className="mt-2 text-lg font-medium">{stock?.industry ?? 'N/A'}</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <p className="text-xs text-zinc-400">Latest Recommendation</p>
          <p className="mt-2 text-lg font-medium">{stock?.latest_recommendation?.action ?? 'N/A'}</p>
        </div>
      </section>

      <StockPriceChart history={history} />

      <section className="mt-10 rounded-xl border border-zinc-800 bg-zinc-950 p-6">
        <h2 className="text-xl font-semibold">Financial Data Snapshot</h2>
        <p className="mt-2 text-sm text-zinc-400">
          Company-level snapshot from the latest available market and profile data.
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-zinc-800 bg-black p-3">
            <p className="text-xs text-zinc-400">Ticker</p>
            <p className="mt-1 font-medium">{stock?.symbol ?? 'N/A'}</p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-black p-3">
            <p className="text-xs text-zinc-400">Exchange</p>
            <p className="mt-1 font-medium">{stock?.exchange ?? 'N/A'}</p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-black p-3">
            <p className="text-xs text-zinc-400">Sector / Industry</p>
            <p className="mt-1 font-medium">{stock?.sector ?? 'N/A'} / {stock?.industry ?? 'N/A'}</p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-black p-3">
            <p className="text-xs text-zinc-400">Latest Price Date</p>
            <p className="mt-1 font-medium">{stock?.latest_price_date ?? 'N/A'}</p>
          </div>
        </div>
      </section>

      <StockDetailTabs
        stock={stock}
        history={history}
        dcfScenarios={dcfScenarios}
        momentumBadge={momentumBadge}
        closeDelta={closeDelta}
        weekDelta={weekDelta}
        symbol={symbol}
      />
    </main>
  );
}
