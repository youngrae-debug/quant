export default function MethodologyPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-3xl font-semibold">About Methodology</h1>
      <p className="mt-4 text-slate-300">
        Trust comes from transparency. Our process is point-in-time by design: features are computed only from information available on each observation date.
      </p>
      <div className="mt-8 space-y-6 text-slate-300">
        <section>
          <h2 className="text-xl font-medium text-white">1) Data Integrity</h2>
          <p className="mt-2">We normalize SEC and market data feeds, preserve filing timestamps, and materialize daily snapshots to prevent look-ahead bias.</p>
        </section>
        <section>
          <h2 className="text-xl font-medium text-white">2) Factor Model</h2>
          <p className="mt-2">Each symbol receives value, growth, profitability, momentum, and expectation sub-scores, followed by sector-relative ranking.</p>
        </section>
        <section>
          <h2 className="text-xl font-medium text-white">3) Recommendation Policy</h2>
          <p className="mt-2">Final scores map to standardized ratings with cooldown constraints and streak tracking to reduce churn.</p>
        </section>

        <section>
          <h2 className="text-xl font-medium text-white">4) Financial Data Layer (Expanded)</h2>
          <ul className="mt-2 list-disc space-y-2 pl-6">
            <li>Point-in-time revenue, EPS, valuation ratios, and profitability metrics are stored by filing date to avoid look-ahead bias.</li>
            <li>Restatement-aware updates keep historical snapshots auditable instead of silently overwriting the past.</li>
            <li>Each metric includes freshness and source lineage so users can quickly assess data trustworthiness.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-medium text-white">5) Institutional Ownership Signals</h2>
          <ul className="mt-2 list-disc space-y-2 pl-6">
            <li>Track ownership concentration and recent institutional accumulation/distribution trends.</li>
            <li>Highlight changes in high-conviction holders and potential crowding risks.</li>
            <li>Blend ownership momentum with price/fundamental context to avoid one-dimensional signals.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-medium text-white">6) Metrics Engine</h2>
          <ul className="mt-2 list-disc space-y-2 pl-6">
            <li>Unified scoring engine combines fundamentals, momentum, expectation, and ownership-derived signals.</li>
            <li>Factor-level contribution view explains exactly what moved a score up or down.</li>
            <li>Stability controls (cooldown, confidence bands, drift checks) reduce noisy recommendation flips.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-medium text-white">How We Differentiate from Similar Sites</h2>
          <ul className="mt-2 list-disc space-y-2 pl-6">
            <li><span className="font-medium text-white">Explainability-first:</span> every recommendation is paired with factor breakdown and rationale, not just a score.</li>
            <li><span className="font-medium text-white">Change-focused UX:</span> users see what changed since the previous run (new filing, ownership shift, momentum break).</li>
            <li><span className="font-medium text-white">Trust badges:</span> each symbol can expose data freshness, source quality, and model confidence in one place.</li>
            <li><span className="font-medium text-white">Actionable workflows:</span> watchlists, alerting, and review queues can turn insights into repeatable decisions.</li>
          </ul>
        </section>
      </div>
    </main>
  );
}
