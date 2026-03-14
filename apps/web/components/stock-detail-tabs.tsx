'use client';

import { useMemo, useState } from 'react';

import type { PriceHistoryItem, StockDetail } from '@/lib/api';
import { StockCommunity } from '@/components/stock-community';

type DcfScenario = {
  growth: number;
  discount: number;
  impliedPrice: number;
  upside: number | null;
};

type MomentumBadge = { label: string; className: string };

type Props = {
  stock: StockDetail | null;
  history: PriceHistoryItem[];
  dcfScenarios: DcfScenario[];
  momentumBadge: MomentumBadge;
  closeDelta: string;
  weekDelta: string;
  symbol: string;
};

const tabs = ['기본 정보', 'DCF', '버핏식 기업분석', '커뮤니티'] as const;

export function StockDetailTabs({ stock, history, dcfScenarios, momentumBadge, closeDelta, weekDelta, symbol }: Props) {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>('기본 정보');
  const checklist = stock?.buffett_checklist;

  const checks = useMemo(() => {
    const hasFinancials = Boolean(
      checklist &&
      checklist.financial_years_available >= 5 &&
      checklist.revenue_ttm != null &&
      checklist.ebit_ttm != null &&
      checklist.free_cash_flow_ttm != null &&
      checklist.roic_ttm != null,
    );

    const hasDebtQuality = Boolean(
      checklist &&
      checklist.total_debt != null &&
      checklist.net_debt != null &&
      checklist.interest_coverage != null &&
      checklist.debt_maturity_profile,
    );

    const hasCapitalAllocation = Boolean(
      checklist && checklist.dividends_ttm != null && checklist.buybacks_ttm != null && checklist.capex_ttm != null,
    );

    return { hasFinancials, hasDebtQuality, hasCapitalAllocation };
  }, [checklist]);

  return (
    <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950 p-6">
      <div className="flex flex-wrap gap-2 border-b border-zinc-800 pb-4">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`rounded-md px-3 py-2 text-sm ${activeTab === tab ? 'bg-white text-black' : 'bg-black text-zinc-300'}`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === '기본 정보' ? (
        <div className="mt-4 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">Institutional Ownership Signals</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-zinc-800 bg-black p-3">
                <p className="text-xs text-zinc-400">1D Close Change</p>
                <p className="mt-1 text-lg font-medium">{closeDelta}</p>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-black p-3">
                <p className="text-xs text-zinc-400">~1W Close Change</p>
                <p className="mt-1 text-lg font-medium">{weekDelta}</p>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-black p-3">
                <p className="text-xs text-zinc-400">Signal State</p>
                <span className={`mt-1 inline-flex rounded-full border px-2 py-1 text-xs ${momentumBadge.className}`}>
                  {momentumBadge.label}
                </span>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold">Metrics Engine View</h2>
            <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-zinc-300">
              <li>Current action: <span className="font-medium text-white">{stock?.latest_recommendation?.action ?? 'N/A'}</span></li>
              <li>Recommendation date: <span className="font-medium text-white">{stock?.latest_recommendation?.recommendation_date ?? 'N/A'}</span></li>
              <li>Conviction: <span className="font-medium text-white">{stock?.latest_recommendation?.conviction != null ? stock.latest_recommendation.conviction.toFixed(2) : 'N/A'}</span></li>
              <li>Most recent close trend: <span className="font-medium text-white">{momentumBadge.label}</span></li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">Recent Price History</h2>
            <div className="mt-4 overflow-x-auto rounded-xl border border-zinc-800">
              <table className="min-w-[720px] w-full text-sm">
                <thead className="bg-zinc-950 text-zinc-300">
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
                    <tr key={row.price_date} className="border-t border-zinc-800">
                      <td className="px-4 py-3 text-zinc-400">{row.price_date}</td>
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
        </div>
      ) : null}

      {activeTab === 'DCF' ? (
        <section className="mt-4">
          <h2 className="text-xl font-semibold">DCF Sensitivity (Scenario Range)</h2>
          <p className="mt-2 text-sm text-zinc-400">Scenario-based valuation range using growth/discount sensitivity (proxy model).</p>
          {dcfScenarios.length === 0 ? (
            <p className="mt-4 text-sm text-zinc-400">Insufficient price data for DCF range.</p>
          ) : (
            <div className="mt-4 overflow-x-auto rounded-lg border border-zinc-800">
              <table className="min-w-[720px] w-full text-sm">
                <thead className="bg-zinc-950 text-zinc-300">
                  <tr>
                    <th className="px-4 py-3 text-left">Growth</th>
                    <th className="px-4 py-3 text-left">Discount</th>
                    <th className="px-4 py-3 text-right">Implied Price</th>
                    <th className="px-4 py-3 text-right">Upside vs Close</th>
                  </tr>
                </thead>
                <tbody>
                  {dcfScenarios.map((scenario) => (
                    <tr key={`${scenario.growth}-${scenario.discount}`} className="border-t border-zinc-800">
                      <td className="px-4 py-3">{(scenario.growth * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3">{(scenario.discount * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-right font-medium">{scenario.impliedPrice.toFixed(2)}</td>
                      <td className={`px-4 py-3 text-right ${scenario.upside != null && scenario.upside >= 0 ? 'text-white' : 'text-rose-300'}`}>
                        {scenario.upside != null ? `${scenario.upside > 0 ? '+' : ''}${scenario.upside.toFixed(2)}%` : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : null}

      {activeTab === '버핏식 기업분석' ? (
        <section className="mt-4">
          <h2 className="text-xl font-semibold">Buffett-style Company Checklist</h2>
          <p className="mt-2 text-sm text-zinc-400">체크리스트를 실제 기업 데이터로 평가합니다.</p>
          <ul className="mt-4 space-y-2 text-sm text-zinc-300">
            <li>{checks.hasFinancials ? '✅' : '❌'} 5~10년 재무제표(수익, EBIT, FCF, ROIC): {checks.hasFinancials ? '충족' : '미충족'}</li>
            <li>{checks.hasDebtQuality ? '✅' : '❌'} 부채 품질(순채무, 이자 보장, 만기): {checks.hasDebtQuality ? '충족' : '미충족'}</li>
            <li>{checks.hasCapitalAllocation ? '✅' : '❌'} 관리 자본 배분 이력: {checks.hasCapitalAllocation ? '충족' : '미충족'}</li>
          </ul>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 text-sm">
            <div className="rounded-lg border border-zinc-800 bg-black p-3">재무 연도 수: <span className="font-medium text-white">{checklist?.financial_years_available ?? 0}년</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">Revenue TTM: <span className="font-medium text-white">{checklist?.revenue_ttm ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">EBIT TTM: <span className="font-medium text-white">{checklist?.ebit_ttm ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">FCF TTM: <span className="font-medium text-white">{checklist?.free_cash_flow_ttm ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">ROIC TTM: <span className="font-medium text-white">{checklist?.roic_ttm ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">Net Debt: <span className="font-medium text-white">{checklist?.net_debt ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">Interest Coverage: <span className="font-medium text-white">{checklist?.interest_coverage ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">Debt Maturity: <span className="font-medium text-white">{checklist?.debt_maturity_profile ?? 'N/A'}</span></div>
            <div className="rounded-lg border border-zinc-800 bg-black p-3">Dividends/Buybacks/Capex: <span className="font-medium text-white">{checklist?.dividends_ttm ?? 'N/A'} / {checklist?.buybacks_ttm ?? 'N/A'} / {checklist?.capex_ttm ?? 'N/A'}</span></div>
          </div>
        </section>
      ) : null}

      {activeTab === '커뮤니티' ? (
        <section className="mt-4">
          <StockCommunity symbol={symbol.toUpperCase()} />
        </section>
      ) : null}
    </section>
  );
}
