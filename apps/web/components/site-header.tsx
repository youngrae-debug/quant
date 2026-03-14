import Link from 'next/link';
import { ThemeToggle } from '@/components/theme-toggle';

const nav = [
  { href: '/', label: '리서치 홈' },
  { href: '/top-picks', label: '모델 추천' },
  { href: '/rankings', label: '종목 랭킹' },
  { href: '/turnarounds', label: '턴어라운드' },
  { href: '/about-methodology', label: '방법론' },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-zinc-800 bg-black/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="text-sm font-semibold tracking-[0.16em] text-white">
          WATS RESEARCH
        </Link>
        <div className="flex items-center gap-4 rounded-lg border border-zinc-800 bg-zinc-950/80 px-3 py-2">
          <nav className="flex gap-1 text-sm text-zinc-300">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-md px-2.5 py-1.5 transition hover:bg-white hover:text-black"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
