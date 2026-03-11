'use client';

import { useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.dataset.theme = theme;
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('dark');

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
      className="rounded border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
      aria-label={`Switch to ${nextTheme} theme`}
      title={`Switch to ${nextTheme} theme`}
    >
      {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}
