import Link from 'next/link';

const nav = [
  { href: '/', label: 'Home' },
  { href: '/top-picks', label: 'Top Picks' },
  { href: '/rankings', label: 'Rankings' },
  { href: '/turnarounds', label: 'Turnarounds' },
  { href: '/about-methodology', label: 'Methodology' },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-sm font-semibold tracking-[0.2em] text-emerald-300">
          QUANT RESEARCH
        </Link>
        <nav className="flex gap-5 text-sm text-slate-300">
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-white">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
