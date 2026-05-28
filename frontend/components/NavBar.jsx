'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const LINKS = [
  { href: '/', label: '首页' },
  { href: '/search', label: '懂你 · AI 导航', highlight: true },
  { href: '/rankings', label: '排行榜' },
  { href: '/earn', label: '我要赚钱' },
  { href: '/admin/analytics', label: '数据看板' },
  {
    href: 'https://github.com/chenyujing1234-netizen/trueAI',
    label: '开源',
    external: true,
    github: true,
  },
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
            const active = !l.external && pathname === l.href;
            const className = [
              'inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm transition',
              active
                ? 'bg-white/10 text-white'
                : 'text-white/70 hover:bg-white/5 hover:text-white',
              l.highlight ? 'font-semibold text-neon-cyan' : '',
              l.github
                ? 'border border-white/15 font-semibold text-neon-lime hover:border-neon-lime/60'
                : '',
            ].join(' ');

            const content = (
              <>
                {l.github ? (
                  <svg
                    viewBox="0 0 24 24"
                    className="h-4 w-4"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path d="M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.16c-3.2.7-3.88-1.37-3.88-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.71.08-.71 1.16.08 1.78 1.2 1.78 1.2 1.04 1.79 2.72 1.27 3.39.97.1-.75.41-1.27.74-1.56-2.55-.29-5.24-1.28-5.24-5.71 0-1.26.45-2.29 1.2-3.1-.12-.3-.52-1.49.11-3.11 0 0 .97-.31 3.18 1.18a11.04 11.04 0 0 1 5.79 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.62.23 2.81.11 3.11.75.81 1.2 1.84 1.2 3.1 0 4.44-2.7 5.42-5.27 5.7.42.36.79 1.08.79 2.18v3.23c0 .31.21.68.8.56C20.21 21.39 23.5 17.07 23.5 12 23.5 5.73 18.27.5 12 .5z" />
                  </svg>
                ) : null}
                <span>{l.label}</span>
                {l.external ? (
                  <span className="text-[10px] text-white/40" aria-hidden>
                    ↗
                  </span>
                ) : null}
              </>
            );

            return l.external ? (
              <a
                key={l.href}
                href={l.href}
                target="_blank"
                rel="noopener noreferrer"
                title="GitHub 仓库 — 在新标签页打开"
                className={className}
              >
                {content}
              </a>
            ) : (
              <Link key={l.href} href={l.href} className={className}>
                {content}
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
