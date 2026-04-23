'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const LINKS = [
  { href: '/', label: '首页' },
  { href: '/search', label: '懂你 · AI 导航', highlight: true },
  { href: '/rankings', label: '排行榜' },
  { href: '/earn', label: '我要赚钱' },
];

export default function NavBar() {
  const pathname = usePathname();
  return (
    <nav className="sticky top-0 z-40 border-b border-white/5 bg-ink-950/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue shadow-glow">
            <span className="text-lg font-black text-white">真</span>
          </div>
          <div className="leading-tight">
            <div className="text-lg font-black tracking-tight">
              真选<span className="neon-text">AI</span>
            </div>
            <div className="text-[10px] text-white/50">TrueAI · 懂你的 AI 导航</div>
          </div>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {LINKS.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={[
                  'rounded-full px-4 py-2 text-sm transition',
                  active
                    ? 'bg-white/10 text-white'
                    : 'text-white/70 hover:bg-white/5 hover:text-white',
                  l.highlight ? 'font-semibold text-neon-cyan' : '',
                ].join(' ')}
              >
                {l.label}
              </Link>
            );
          })}
        </div>

        <Link href="/search" className="btn-primary text-sm">
          开始懂你
          <span aria-hidden>→</span>
        </Link>
      </div>
    </nav>
  );
}
