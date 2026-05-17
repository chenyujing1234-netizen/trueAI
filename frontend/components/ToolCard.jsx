'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { useCompareStore } from '@/lib/compareStore';

function LogoBox({ src, name }) {
  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className="h-10 w-10 rounded-xl bg-white/10 object-contain p-1"
        onError={(e) => {
          e.currentTarget.style.display = 'none';
        }}
      />
    );
  }
  return (
    <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue text-sm font-black">
      {name?.[0] ?? '?'}
    </div>
  );
}

export default function ToolCard({ tool, index = 0, hangeffect = false }) {
  const ids = useCompareStore((s) => s.ids);
  const toggle = useCompareStore((s) => s.toggle);
  const selected = ids.includes(tool.id);

  const swingRange = hangeffect ? [-1.6, 1.6] : [0, 0];
  const durBase = 3.2 + (index % 5) * 0.4;

  return (
    <div className="flex flex-col items-stretch">
      {hangeffect && (
        <div className="mx-auto h-8 flex justify-center">
          <div className="rope" />
        </div>
      )}
      <motion.div
        initial={false}
        className="origin-top card-appear"
        style={{
          transformOrigin: 'top center',
          animationDelay: `${index * 30}ms`,
        }}
      >
        <motion.div
          animate={hangeffect ? { rotate: swingRange } : { rotate: 0 }}
          transition={{
            duration: durBase,
            repeat: hangeffect ? Infinity : 0,
            repeatType: 'reverse',
            ease: 'easeInOut',
          }}
          className="glass glass-hover relative flex h-full flex-col gap-3 rounded-2xl p-4 transition"
          whileHover={{ y: -4 }}
        >
          <Link href={`/tool/${tool.slug}`} className="flex items-start gap-3">
            <LogoBox src={tool.logo_url} name={tool.name} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <h3 className="truncate text-base font-bold text-white">{tool.name}</h3>
                <div className="text-right leading-tight">
                  <div className="text-xl font-black neon-text">
                    {Number(tool.overall_score || 0).toFixed(1)}
                  </div>
                  <div className="text-[10px] text-white/40">综合</div>
                </div>
              </div>
              <p className="mt-1 line-clamp-2 text-xs text-white/65">
                {tool.tagline || '暂无一句话简介'}
              </p>
            </div>
          </Link>

          <div className="flex flex-wrap gap-1.5">
            {tool.is_free && <span className="chip text-neon-lime">免费</span>}
            {!tool.is_free && <span className="chip text-neon-pink">付费</span>}
            {tool.need_vpn ? (
              <span className="chip text-neon-purple">需魔法</span>
            ) : (
              <span className="chip text-neon-cyan">国内直连</span>
            )}
            {tool.form_factor && <span className="chip">{formFactorLabel(tool.form_factor)}</span>}
            {(tool.categories || []).slice(0, 2).map((c) => (
              <span key={c} className="chip text-white/60">
                #{c}
              </span>
            ))}
          </div>

          <div className="flex items-center justify-between border-t border-white/5 pt-2">
            <span className="text-[11px] text-white/40">
              {tool.review_count > 0 ? `${tool.review_count} 条评测` : '等你第一个评测'}
            </span>
            <button
              onClick={(e) => {
                e.preventDefault();
                toggle(tool);
              }}
              className={[
                'rounded-full px-2.5 py-1 text-[11px] transition',
                selected
                  ? 'bg-neon-pink/20 text-neon-pink'
                  : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white',
              ].join(' ')}
            >
              {selected ? '✓ 已加入对比' : '加入对比'}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

function formFactorLabel(f) {
  return (
    {
      saas: '网页版',
      mobile: 'App',
      cli: 'CLI',
      windows_app: '桌面端',
      web: '插件',
    }[f] || f
  );
}
