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
      </div>
    </main>
  );
}
