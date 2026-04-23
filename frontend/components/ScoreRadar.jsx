'use client';

const DIMS = [
  { k: 'overall_score', label: '综合' },
  { k: 'usability_score', label: '可用性' },
  { k: 'effect_score', label: '效果' },
  { k: 'price_score', label: '性价比' },
  { k: 'speed_score', label: '速度' },
];

export default function ScoreRadar({ tool, max = 10 }) {
  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-5">
      {DIMS.map((d) => {
        const v = Number(tool[d.k] || 0);
        const pct = Math.max(0, Math.min(100, (v / max) * 100));
        return (
          <div key={d.k} className="min-w-0">
            <div className="flex items-baseline justify-between">
              <span className="text-xs text-white/60">{d.label}</span>
              <span className="text-sm font-bold neon-text tabular-nums">{v.toFixed(1)}</span>
            </div>
            <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
              <div
                className="h-full rounded-full bg-gradient-to-r from-neon-purple to-neon-cyan"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
