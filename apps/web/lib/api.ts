export type Health = { status: string };
export type Recommendation = {
  symbol: string;
  recommendation_date: string;
  action: string;
  conviction: number | null;
  target_price: number | null;
  horizon_days: number | null;
  rationale: string | null;
};

export type Ranking = {
  symbol: string;
  score_date: string;
  final_score: number;
};

export type StockDetail = {
  symbol: string;
  name: string | null;
  exchange: string | null;
  sector: string | null;
  industry: string | null;
  cik: string | null;
  sic: string | null;
  latest_close: number | null;
  latest_price_date: string | null;
  latest_recommendation: Recommendation | null;
};

export type PriceHistoryItem = {
  price_date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  adjusted_close: number | null;
  volume: number | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function getHealth(): Promise<Health | null> {
  return request<Health>('/health');
}

export async function getTopPicks(): Promise<Recommendation[]> {
  const data = await request<{ items: Recommendation[] }>('/top-picks?page=1&size=10');
  return data?.items ?? [
    { symbol: 'MSFT', recommendation_date: '2026-03-09', action: 'buy', conviction: 0.82, target_price: 530, horizon_days: 180, rationale: 'AI monetization + margin resilience' },
    { symbol: 'NVDA', recommendation_date: '2026-03-09', action: 'buy', conviction: 0.8, target_price: 1450, horizon_days: 180, rationale: 'Datacenter demand durability' },
  ];
}

export async function getRankings(): Promise<Ranking[]> {
  const data = await request<{ items: Ranking[] }>('/rankings?page=1&size=20');
  return data?.items ?? [
    { symbol: 'MSFT', score_date: '2026-03-09', final_score: 91.2 },
    { symbol: 'NVDA', score_date: '2026-03-09', final_score: 89.4 },
    { symbol: 'META', score_date: '2026-03-09', final_score: 84.8 },
  ];
}

export async function getStock(symbol: string): Promise<StockDetail | null> {
  const data = await request<StockDetail>(`/stocks/${symbol}`);
  if (data) return data;
  return {
    symbol: symbol.toUpperCase(),
    name: 'Sample Corp',
    exchange: 'NASDAQ',
    sector: 'Technology',
    industry: 'Software',
    cik: null,
    sic: null,
    latest_close: 123.45,
    latest_price_date: '2026-03-09',
    latest_recommendation: null,
  };
}

export async function getStockHistory(symbol: string): Promise<PriceHistoryItem[]> {
  const data = await request<{ items: PriceHistoryItem[] }>(`/stocks/${symbol}/history?page=1&size=30`);
  return data?.items ?? [];
}
