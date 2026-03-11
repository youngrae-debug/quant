'use client';

import { useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.dataset.theme = theme;
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('light');

  useEffect(() => {
    const saved = window.localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') {
      setTheme(saved);
      applyTheme(saved);
      return;
    }

    const systemTheme: Theme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    setTheme(systemTheme);
    applyTheme(systemTheme);
  }, []);

  const nextTheme: Theme = theme === 'dark' ? 'light' : 'dark';

  return (
    <button
      type="button"
      onClick={() => {
        setTheme(nextTheme);
        applyTheme(nextTheme);
        window.localStorage.setItem('theme', nextTheme);
      }}
      className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 shadow-[4px_4px_10px_rgba(148,163,184,0.16),-4px_-4px_10px_rgba(255,255,255,0.9)] transition hover:border-emerald-400 hover:text-emerald-300"
      aria-label={`Switch to ${nextTheme} theme`}
      title={`Switch to ${nextTheme} theme`}
    >
      {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}
