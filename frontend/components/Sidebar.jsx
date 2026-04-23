'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar({ categories = [], activeSlug }) {
  const pathname = usePathname();
  return (
    <aside className="glass scrollbar-thin sticky top-20 hidden max-h-[calc(100vh-6rem)] overflow-y-auto rounded-2xl p-3 md:block md:w-56">
      <div className="px-2 pb-2 text-xs uppercase tracking-widest text-white/40">分类</div>
      <nav className="flex flex-col gap-1">
        <Link
          href="/"
          className={[
            'group flex items-center justify-between rounded-xl px-3 py-2 text-sm transition',
            pathname === '/' && !activeSlug
              ? 'bg-gradient-to-r from-neon-purple/25 to-neon-blue/15 text-white'
              : 'text-white/75 hover:bg-white/5 hover:text-white',
          ].join(' ')}
        >
          <span className="flex items-center gap-2">
            <span>⭐</span>
            <span>全部</span>
          </span>
        </Link>
        {categories.map((c) => {
          const active = activeSlug === c.slug;
          return (
            <Link
              key={c.slug}
              href={`/category/${c.slug}`}
              className={[
                'group flex items-center justify-between rounded-xl px-3 py-2 text-sm transition',
                active
                  ? 'bg-gradient-to-r from-neon-purple/25 to-neon-blue/15 text-white'
                  : 'text-white/75 hover:bg-white/5 hover:text-white',
              ].join(' ')}
            >
              <span className="flex items-center gap-2">
                <span>{c.icon || '•'}</span>
                <span>{c.name}</span>
              </span>
              <span className="text-[11px] text-white/40 group-hover:text-white/70">
                {c.tool_count}
              </span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
