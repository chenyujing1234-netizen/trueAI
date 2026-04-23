'use client';

import { useCompareStore } from '@/lib/compareStore';

export default function AddToCompareButton({ tool, className = '' }) {
  const ids = useCompareStore((s) => s.ids);
  const toggle = useCompareStore((s) => s.toggle);
  const selected = ids.includes(tool.id);
  return (
    <button
      onClick={() => toggle(tool)}
      className={[
        'btn-ghost',
        selected ? 'bg-neon-pink/20 text-neon-pink border-neon-pink/40' : '',
        className,
      ].join(' ')}
    >
      {selected ? '✓ 已加入对比' : '加入对比（≤3）'}
    </button>
  );
}
