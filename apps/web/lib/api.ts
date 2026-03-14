export type Health = { status: string };
export type Recommendation = {
  symbol: string;
  name: string | null;
  recommendation_date: string;
  action: string;
  conviction: number | null;
  target_price: number | null;
  horizon_days: number | null;
  rationale: string | null;
};

export type Ranking = {
  symbol: string;
  name: string | null;
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

export type PaginationMeta = {
  page: number;
  size: number;
  total: number;
};

export type PaginatedRecommendations = {
  items: Recommendation[];
  meta: PaginationMeta;
};

export type PaginatedRankings = {
  items: Ranking[];
  meta: PaginationMeta;
};

export type Turnaround = {
  symbol: string;
  name: string | null;
  base_year: number;
  next_year: number;
  turnaround_year: number;
  base_year_net_income: number;
  turnaround_year_net_income: number;
};

export type PaginatedTurnarounds = {
  items: Turnaround[];
  meta: PaginationMeta;
};

export type StockComment = {
  id: number;
  symbol: string;
  nickname: string;
  content: string;
  created_at: string;
};

export type PaginatedStockComments = {
  items: StockComment[];
  meta: PaginationMeta;
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

export async function getTopPicks(page = 1, size = 50, q?: string): Promise<PaginatedRecommendations> {
  const safePage = Number.isFinite(page) && page > 0 ? Math.floor(page) : 1;
  const safeSize = Number.isFinite(size) && size > 0 ? Math.min(100, Math.floor(size)) : 50;
  const query = q?.trim() ? `&q=${encodeURIComponent(q.trim())}` : '';
  const data = await request<PaginatedRecommendations>(`/top-picks?page=${safePage}&size=${safeSize}${query}`);
  return data ?? { items: [], meta: { page: safePage, size: safeSize, total: 0 } };
}

export async function getRankings(page = 1, size = 50, q?: string): Promise<PaginatedRankings> {
  const safePage = Number.isFinite(page) && page > 0 ? Math.floor(page) : 1;
  const safeSize = Number.isFinite(size) && size > 0 ? Math.min(100, Math.floor(size)) : 50;
  const query = q?.trim() ? `&q=${encodeURIComponent(q.trim())}` : '';
  const data = await request<PaginatedRankings>(`/rankings?page=${safePage}&size=${safeSize}${query}`);
  return data ?? { items: [], meta: { page: safePage, size: safeSize, total: 0 } };
}

export async function getStock(symbol: string): Promise<StockDetail | null> {
  const data = await request<StockDetail>(`/stocks/${symbol}`);
  return data;
}

export async function getStockHistory(symbol: string, size = 180): Promise<PriceHistoryItem[]> {
  const safeSize = Number.isFinite(size) && size > 0 ? Math.min(500, Math.floor(size)) : 180;
  const data = await request<{ items: PriceHistoryItem[] }>(`/stocks/${symbol}/history?page=1&size=${safeSize}`);
  return data?.items ?? [];
}


export async function getTurnarounds(page = 1, size = 50): Promise<PaginatedTurnarounds> {
  const safePage = Number.isFinite(page) && page > 0 ? Math.floor(page) : 1;
  const safeSize = Number.isFinite(size) && size > 0 ? Math.min(100, Math.floor(size)) : 50;
  const data = await request<PaginatedTurnarounds>(`/turnarounds?page=${safePage}&size=${safeSize}`);
  return data ?? { items: [], meta: { page: safePage, size: safeSize, total: 0 } };
}

export async function getStockComments(symbol: string, page = 1, size = 20): Promise<PaginatedStockComments> {
  const safePage = Number.isFinite(page) && page > 0 ? Math.floor(page) : 1;
  const safeSize = Number.isFinite(size) && size > 0 ? Math.min(100, Math.floor(size)) : 20;
  const data = await request<PaginatedStockComments>(`/stocks/${symbol}/comments?page=${safePage}&size=${safeSize}`);
  return data ?? { items: [], meta: { page: safePage, size: safeSize, total: 0 } };
}

export async function postStockComment(symbol: string, nickname: string, content: string): Promise<StockComment | null> {
  try {
    const res = await fetch(`${API_BASE}/stocks/${symbol}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname, content }),
    });
    if (!res.ok) return null;
    return (await res.json()) as StockComment;
  } catch {
    return null;
  }
}
