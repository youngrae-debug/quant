'use client';

import { useEffect, useMemo, useState } from 'react';

type HealthResponse = {
  status: string;
};

export default function HomePage() {
  const apiBaseUrl = useMemo(
    () => process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
    []
  );

  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function fetchHealth() {
      try {
        const response = await fetch(`${apiBaseUrl}/health`, { cache: 'no-store' });

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const data = (await response.json()) as HealthResponse;
        if (active) {
          setHealth(data);
          setError(null);
        }
      } catch (fetchError) {
        if (active) {
          setError(fetchError instanceof Error ? fetchError.message : 'Unknown error');
        }
      }
    }

    fetchHealth();

    return () => {
      active = false;
    };
  }, [apiBaseUrl]);

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl items-center px-6 py-16">
      <section className="space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">Quant Research Platform</h1>
        <p className="text-slate-300">API base URL: {apiBaseUrl}</p>
        <div className="rounded-lg border border-slate-700 bg-slate-900/70 p-4 text-sm">
          {health && <p>API health status: {health.status}</p>}
          {!health && !error && <p>Checking API health…</p>}
          {error && <p className="text-red-300">API health check failed: {error}</p>}
        </div>
      </section>
    </main>
  );
}
