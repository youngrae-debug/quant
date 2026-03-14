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
      <div className="mx-auto max-w-6xl px-4 py-3 sm:px-6 sm:py-4">
        <div className="flex items-center justify-between gap-3">
          <Link href="/" className="text-xs font-semibold tracking-[0.16em] text-white sm:text-sm">
            WATS RESEARCH
          </Link>
          <ThemeToggle />
        </div>

        <nav className="mt-3 flex gap-1 overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-950/80 p-1.5 text-sm text-zinc-300 md:mt-4 md:justify-center md:gap-2 md:p-2">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="whitespace-nowrap rounded-md px-2.5 py-1.5 transition hover:bg-white hover:text-black md:px-3"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
