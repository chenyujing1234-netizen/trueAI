'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function ReviewList({ toolId }) {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    api
      .reviews(toolId)
      .then((rs) => alive && setReviews(rs))
      .catch(() => alive && setReviews([]))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [toolId]);

  if (loading) return <div className="text-sm text-white/50">加载评测中...</div>;
  if (!reviews.length) {
    return (
      <div className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-white/60">
        还没有人评测过这个工具 —— <span className="text-neon-lime">你可以成为第一个！</span>
        <br />通过后可获得现金奖励。
      </div>
    );
  }
  return (
    <ul className="flex flex-col gap-4">
      {reviews.map((r) => (
        <li key={r.id} className="glass rounded-2xl p-4">
          <div className="mb-2 flex items-center justify-between">
            <div className="text-sm">
              <span className="font-bold text-white">{r.username || '匿名用户'}</span>
              <span className="ml-2 text-xs text-white/40">
                {new Date(r.created_at).toLocaleDateString('zh-CN')}
              </span>
            </div>
            <div className="text-lg font-black neon-text">{Number(r.score).toFixed(1)}</div>
          </div>
          <p className="whitespace-pre-wrap text-sm text-white/80">{r.content}</p>
        </li>
      ))}
    </ul>
  );
}
