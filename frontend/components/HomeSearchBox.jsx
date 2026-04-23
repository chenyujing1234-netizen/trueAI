'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

const SUGGESTIONS = [
  '我是新手，想学编程，推荐一个免费的 AI 工具',
  '小红书博主，想做图文封面',
  '国内直连的 AI 搜索，要有引用',
  '做 PPT 的 AI，最好一句话生成',
];

export default function HomeSearchBox() {
  const [q, setQ] = useState('');
  const router = useRouter();

  const go = (text) => {
    const t = (text ?? q).trim();
    if (!t) {
      router.push('/search');
      return;
    }
    router.push(`/search?q=${encodeURIComponent(t)}`);
  };

  return (
    <div className="w-full max-w-3xl">
      <div className="glass group flex items-center gap-2 rounded-full p-2 pl-5 shadow-glow">
        <span className="text-neon-cyan">✦</span>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && go()}
          placeholder={'告诉"懂你" —— 你要做什么，比如：我想给公众号配封面图'}
          className="min-w-0 flex-1 bg-transparent py-2 text-white placeholder:text-white/40 focus:outline-none"
        />
        <button onClick={() => go()} className="btn-primary">
          让"懂你"帮我选 →
        </button>
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="text-white/40">试试：</span>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => go(s)}
            className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-white/70 transition hover:border-neon-purple/60 hover:text-white"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
