'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useMemo } from 'react';

const SORTS = [
  { v: 'overall', l: '综合评分' },
  { v: 'usability', l: '可用性' },
  { v: 'effect', l: '效果' },
  { v: 'price', l: '性价比' },
  { v: 'speed', l: '速度' },
  { v: 'reviews', l: '评测数' },
  { v: 'new', l: '最新上线' },
];

const FORM_FACTORS = [
  { v: '', l: '全部形态' },
  { v: 'saas', l: '网页 SaaS' },
  { v: 'mobile', l: 'App' },
  { v: 'cli', l: 'CLI' },
  { v: 'windows_app', l: '桌面端' },
];

const AUDIENCES = [
  { v: '', l: '全部人群' },
  { v: 'beginner', l: '小白' },
  { v: 'developer', l: '开发者' },
  { v: 'student', l: '学生' },
  { v: 'designer', l: '设计师' },
  { v: 'creator', l: '创作者' },
];

export default function FilterBar({ basePath }) {
  const router = useRouter();
  const sp = useSearchParams();

  const current = useMemo(
    () => ({
      sort: sp.get('sort') || 'overall',
      form_factor: sp.get('form_factor') || '',
      audience: sp.get('audience') || '',
      free: sp.get('free') || '',
      need_vpn: sp.get('need_vpn') || '',
    }),
    [sp],
  );

  const update = (patch) => {
    const next = new URLSearchParams(sp.toString());
    Object.entries(patch).forEach(([k, v]) => {
      if (v === '' || v === undefined || v === null) next.delete(k);
      else next.set(k, v);
    });
    router.push(`${basePath}?${next.toString()}`);
  };

  const Select = ({ value, onChange, options, label }) => (
    <label className="flex items-center gap-2 text-xs text-white/60">
      <span>{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-full border border-white/10 bg-ink-800 px-3 py-1.5 text-white/90 focus:border-neon-purple focus:outline-none"
      >
        {options.map((o) => (
          <option key={o.v} value={o.v} className="bg-ink-900">
            {o.l}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="glass mb-6 flex flex-wrap items-center gap-3 rounded-2xl p-3">
      <Select
        label="排序"
        value={current.sort}
        onChange={(v) => update({ sort: v })}
        options={SORTS}
      />
      <Select
        label="形态"
        value={current.form_factor}
        onChange={(v) => update({ form_factor: v })}
        options={FORM_FACTORS}
      />
      <Select
        label="人群"
        value={current.audience}
        onChange={(v) => update({ audience: v })}
        options={AUDIENCES}
      />
      <Select
        label="免费"
        value={current.free}
        onChange={(v) => update({ free: v })}
        options={[
          { v: '', l: '不限' },
          { v: 'true', l: '仅免费' },
          { v: 'false', l: '仅付费' },
        ]}
      />
      <Select
        label="网络"
        value={current.need_vpn}
        onChange={(v) => update({ need_vpn: v })}
        options={[
          { v: '', l: '不限' },
          { v: 'false', l: '国内直连' },
          { v: 'true', l: '需魔法' },
        ]}
      />
    </div>
  );
}
