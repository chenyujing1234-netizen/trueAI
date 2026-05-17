'use client';

import { useEffect, useState } from 'react';

const SOURCE_LABEL = {
  watcha: { name: '观猹', url: 'https://watcha.cn', color: 'text-orange-400' },
};

function Avatar({ src, name }) {
  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className="h-9 w-9 rounded-full object-cover ring-2 ring-white/10"
        onError={(e) => { e.target.style.display = 'none'; }}
      />
    );
  }
  const initials = (name || '?').slice(0, 1).toUpperCase();
  return (
    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-500/20 text-sm font-bold text-indigo-300 ring-2 ring-white/10">
      {initials}
    </div>
  );
}

function ReviewCard({ review }) {
  const [expanded, setExpanded] = useState(false);
  const content = review.content || '';
  const shouldClamp = content.length > 160;
  const displayContent = shouldClamp && !expanded ? content.slice(0, 160) + '…' : content;

  return (
    <div className="rounded-2xl bg-white/5 p-4 transition hover:bg-white/8">
      <div className="mb-3 flex items-center gap-3">
        <Avatar src={review.author_avatar} name={review.author_name} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-white/90">
            {review.author_name || '匿名用户'}
          </p>
          {review.external_created_at && (
            <p className="text-xs text-white/40">
              {new Date(review.external_created_at).toLocaleDateString('zh-CN')}
            </p>
          )}
        </div>
        {review.upvotes > 0 && (
          <span className="flex items-center gap-1 rounded-full bg-white/5 px-2 py-0.5 text-xs text-white/50">
            👍 {review.upvotes}
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed text-white/75 whitespace-pre-wrap">
        {displayContent}
      </p>
      {shouldClamp && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-1 text-xs text-indigo-400 hover:text-indigo-300"
        >
          {expanded ? '收起' : '展开全文'}
        </button>
      )}
    </div>
  );
}

export default function ExternalReviews({ toolSlug }) {
  const [reviews, setReviews] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const PAGE_SIZE = 10;

  useEffect(() => {
    if (!toolSlug) return;
    setLoading(true);
    fetch(`/api/tools/${toolSlug}/external-reviews?page=${page}&page_size=${PAGE_SIZE}`)
      .then((r) => r.json())
      .then((d) => {
        setReviews(d.items || []);
        setTotal(d.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [toolSlug, page]);

  if (!loading && total === 0) return null;

  return (
    <section className="glass rounded-3xl p-6">
      {/* 标题栏 */}
      <div className="mb-5 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-white/90">
          用户真实评价
          {total > 0 && (
            <span className="rounded-full bg-indigo-500/20 px-2.5 py-0.5 text-sm font-normal text-indigo-300">
              {total}
            </span>
          )}
        </h2>
        <a
          href={`https://watcha.cn/products/${toolSlug}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 rounded-full bg-orange-500/10 px-3 py-1 text-xs text-orange-400 hover:bg-orange-500/20 transition"
        >
          来源：观猹
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>

      {/* 评论列表 */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-2xl bg-white/5" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {reviews.map((r) => <ReviewCard key={r.id} review={r} />)}
        </div>
      )}

      {/* 分页 */}
      {total > PAGE_SIZE && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage(p => p - 1)}
            className="rounded-full px-3 py-1 text-sm text-white/50 hover:text-white/80 disabled:opacity-30"
          >
            ← 上一页
          </button>
          <span className="text-xs text-white/40">
            第 {page} 页 / 共 {Math.ceil(total / PAGE_SIZE)} 页
          </span>
          <button
            disabled={page >= Math.ceil(total / PAGE_SIZE)}
            onClick={() => setPage(p => p + 1)}
            className="rounded-full px-3 py-1 text-sm text-white/50 hover:text-white/80 disabled:opacity-30"
          >
            下一页 →
          </button>
        </div>
      )}
    </section>
  );
}
