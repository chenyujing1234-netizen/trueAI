'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

function Counter({ value }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const duration = 900;
    const start = performance.now();
    let frame;
    const tick = (t) => {
      const p = Math.min(1, (t - start) / duration);
      setN(Math.round(value * (1 - Math.pow(1 - p, 3))));
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);
  return <span className="font-black tabular-nums">{n}</span>;
}

export default function StatsBar({ stats }) {
  const items = [
    { k: 'tools', label: '已评测智能体', value: stats?.tools ?? 0, suffix: '个' },
    { k: 'categories', label: '覆盖分类', value: stats?.categories ?? 0, suffix: '类' },
    { k: 'reviews', label: '人工评测', value: stats?.reviews ?? 0, suffix: '条' },
  ];
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass flex flex-wrap items-center justify-between gap-4 rounded-2xl px-6 py-4"
    >
      <div className="flex flex-wrap items-center gap-8">
        {items.map((i) => (
          <div key={i.k} className="flex items-baseline gap-1.5">
            <span className="text-2xl md:text-3xl">
              <span className="neon-text">
                <Counter value={i.value} />
              </span>
            </span>
            <span className="text-sm text-white/60">
              {i.suffix} · {i.label}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 text-xs text-white/60">
        <span className="rounded-full bg-neon-lime/15 px-2.5 py-1 text-neon-lime">· 无广告</span>
        <span className="rounded-full bg-neon-cyan/15 px-2.5 py-1 text-neon-cyan">· 实时</span>
        <span className="rounded-full bg-neon-pink/15 px-2.5 py-1 text-neon-pink">· 人工</span>
      </div>
    </motion.div>
  );
}
