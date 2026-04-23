'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import AddToCompareButton from './AddToCompareButton';

const DIMS = [
  { v: 'overall', l: '综合' },
  { v: 'usability', l: '可用性' },
  { v: 'effect', l: '效果' },
  { v: 'price', l: '性价比' },
  { v: 'speed', l: '速度' },
  { v: 'reviews', l: '评测数' },
];

const MEDAL = ['🥇', '🥈', '🥉'];

export default function RankingView({ categories, items, dimension, category }) {
  const router = useRouter();
  const [customQ, setCustomQ] = useState('');

  const update = (patch) => {
    const next = new URLSearchParams();
    if (patch.dimension ?? dimension) next.set('dimension', patch.dimension ?? dimension);
    if (patch.category !== undefined ? patch.category : category) {
      next.set('category', patch.category !== undefined ? patch.category : category);
    }
    router.push(`/rankings?${next.toString()}`);
  };

  return (
    <>
      {/* 控制条 */}
      <div className="glass mb-6 flex flex-col gap-3 rounded-2xl p-4 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-white/50">维度</span>
          {DIMS.map((d) => (
            <button
              key={d.v}
              onClick={() => update({ dimension: d.v })}
              className={[
                'rounded-full px-3 py-1 text-sm transition',
                dimension === d.v
                  ? 'bg-gradient-to-r from-neon-purple to-neon-blue text-white'
                  : 'bg-white/5 text-white/70 hover:bg-white/10',
              ].join(' ')}
            >
              {d.l}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-white/50">分类</span>
          <select
            value={category}
            onChange={(e) => update({ category: e.target.value })}
            className="rounded-full border border-white/10 bg-ink-800 px-3 py-1.5 text-sm text-white/90 focus:outline-none"
          >
            <option value="" className="bg-ink-900">全部分类</option>
            {categories.map((c) => (
              <option key={c.slug} value={c.slug} className="bg-ink-900">
                {c.icon} {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 自然语言专属排名输入 */}
      <div className="glass mb-8 flex flex-col gap-2 rounded-2xl p-4 md:flex-row md:items-center">
        <div className="flex-1 text-sm">
          <div className="text-xs uppercase tracking-widest text-white/40">
            Personalized Ranking
          </div>
          <div className="mt-0.5 text-white/80">
            用一句话描述你的场景，让 <span className="neon-text font-bold">懂你</span> 生成专属排行
          </div>
        </div>
        <input
          value={customQ}
          onChange={(e) => setCustomQ(e.target.value)}
          placeholder="例如：学生党想免费学编程，能不翻墙最好"
          className="min-w-0 flex-1 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white placeholder:text-white/40 focus:border-neon-purple focus:outline-none"
        />
        <Link
          href={customQ.trim() ? `/search?q=${encodeURIComponent(customQ.trim())}` : '/search'}
          className="btn-primary text-sm"
        >
          生成我的专属排名 →
        </Link>
      </div>

      {/* 排行榜列表 */}
      <div className="flex flex-col gap-3">
        {items.length === 0 && (
          <div className="glass rounded-2xl p-10 text-center text-white/60">
            该维度暂无数据。
          </div>
        )}
        {items.map((t) => {
          const top3 = t.rank <= 3;
          return (
            <div
              key={t.id}
              className={[
                'glass glass-hover flex items-center gap-4 rounded-2xl p-4 transition',
                top3 ? 'shadow-glow' : '',
              ].join(' ')}
            >
              <div className="flex w-24 shrink-0 flex-col items-center">
                <div
                  className={[
                    'font-black leading-none tabular-nums',
                    top3 ? 'text-6xl md:text-7xl neon-text' : 'text-4xl text-white/70',
                  ].join(' ')}
                >
                  {t.rank}
                </div>
                {top3 && <div className="mt-1 text-2xl">{MEDAL[t.rank - 1]}</div>}
              </div>

              <Link href={`/tool/${t.slug}`} className="flex min-w-0 flex-1 items-center gap-3">
                {t.logo_url ? (
                  <img
                    src={t.logo_url}
                    alt={t.name}
                    className="h-12 w-12 rounded-xl bg-white/10 object-contain p-1"
                  />
                ) : (
                  <div className="grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue font-black">
                    {t.name?.[0]}
                  </div>
                )}
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="truncate text-lg font-bold text-white">{t.name}</h3>
                    <div className="flex gap-1">
                      {t.is_free && <span className="chip text-neon-lime">免费</span>}
                      {t.need_vpn ? (
                        <span className="chip text-neon-purple">需魔法</span>
                      ) : (
                        <span className="chip text-neon-cyan">直连</span>
                      )}
                    </div>
                  </div>
                  <p className="truncate text-sm text-white/60">{t.tagline || '—'}</p>
                </div>
              </Link>

              <div className="flex flex-col items-end gap-2">
                <div className="text-right">
                  <div className="text-3xl font-black neon-text tabular-nums">
                    {Number(t.dimension_score || t.overall_score || 0).toFixed(1)}
                  </div>
                  <div className="text-[10px] uppercase text-white/40">score</div>
                </div>
                <AddToCompareButton tool={t} className="h-8 px-3 text-xs" />
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
