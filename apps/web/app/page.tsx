import Link from 'next/link';
import { getHealth } from '@/lib/api';

const highlights = [
  {
    title: 'Multi-Factor Scoring Model',
    description:
      'Quality, value, growth, and profitability metrics are standardized into a unified score with reduced sector/size bias.',
  },
  {
    title: 'Momentum & Earnings Revision Monitoring',
    description:
      'Price trend, trading strength, and earnings estimate revisions are tracked together to capture expectation shifts.',
  },
  {
    title: 'Risk-Aware Candidate Management',
    description:
      'Volatility, liquidity, and drawdown signals are incorporated to prioritize ideas on a risk-adjusted basis.',
  },
];

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:py-14">
      <section className="rounded-2xl border border-zinc-700 bg-black p-5 sm:p-7 md:p-10">
        <p className="text-[11px] uppercase tracking-[0.22em] text-zinc-400 sm:text-xs">Institutional Equity Research Console</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:mt-4 sm:text-4xl md:text-5xl">
          Institutional-grade stock research in one place.
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-zinc-300 sm:mt-5 sm:text-base">
          WATS delivers rankings, model recommendations, and turnaround candidates from point-in-time data.
          Every output includes factor-level rationale to improve transparency and repeatability in portfolio decisions.
        </p>

        <div className="mt-6 grid gap-3 sm:mt-8 sm:flex sm:flex-wrap">
          <Link
            href="/top-picks"
            className="w-full rounded-lg bg-white px-5 py-2.5 text-center text-sm font-semibold text-black transition hover:bg-zinc-200 sm:w-auto"
          >
            View Top Picks
          </Link>
          <Link
            href="/about-methodology"
            className="w-full rounded-lg border border-zinc-600 px-5 py-2.5 text-center text-sm font-medium text-zinc-100 transition hover:bg-zinc-900 sm:w-auto"
          >
            Research Methodology
          </Link>
        </div>
      </section>

      <section className="mt-5 grid gap-4 lg:mt-6 lg:grid-cols-[1fr_280px]">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {highlights.map((item) => (
            <article key={item.title} className="rounded-xl border border-zinc-800 bg-zinc-950 p-5">
              <h2 className="text-sm font-semibold text-white">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{item.description}</p>
            </article>
          ))}
        </div>

        <aside className="rounded-xl border border-zinc-800 bg-zinc-950 p-5">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-zinc-500">Research System Status</p>
          <p className="mt-2 text-xl font-semibold text-white">{health?.status ?? 'unavailable'}</p>
          <p className="mt-2 text-sm text-zinc-400">Shows the current state of ingestion, scoring, and recommendation pipelines.</p>
        </aside>
      </section>
    </main>
  );
}
