import Link from 'next/link';
import { api } from '@/lib/api';
import { AUDIENCE_LABELS, FORM_FACTOR_LABELS } from '@/lib/labels';

export const metadata = { title: 'AI 工具对比 · TrueAI' };
export const dynamic = 'force-dynamic';

export default async function ComparePage({ searchParams }) {
  const idsParam = (searchParams?.ids || '').toString();
  const ids = idsParam
    .split(',')
    .map((x) => parseInt(x, 10))
    .filter(Boolean);
  if (ids.length < 1) {
    return (
      <div className="mt-10 text-center text-white/60">
        请先从首页/分类页把 2-3 个工具加入对比 ✨
      </div>
    );
  }

  let tools = [];
  try {
    tools = await api.compare(ids);
  } catch (e) {
    return <div className="mt-10 text-center text-white/60">加载失败：{e.message}</div>;
  }

  const rows = [
    { label: '综合评分', render: (t) => Number(t.overall_score).toFixed(1), big: true },
    { label: '可用性', render: (t) => Number(t.usability_score).toFixed(1) },
    { label: '效果', render: (t) => Number(t.effect_score).toFixed(1) },
    { label: '性价比', render: (t) => Number(t.price_score).toFixed(1) },
    { label: '速度', render: (t) => Number(t.speed_score).toFixed(1) },
    { label: '开发公司', render: (t) => t.developer || '—' },
    { label: '形态', render: (t) => FORM_FACTOR_LABELS[t.form_factor] || t.form_factor },
    { label: '收费', render: (t) => t.pricing_info || (t.is_free ? '免费' : '付费') },
    { label: '需外网', render: (t) => (t.need_vpn ? '是' : '否') },
    { label: '支持 CLI', render: (t) => (t.support_cli ? '是' : '否') },
    { label: '支持 API', render: (t) => (t.support_api ? '是' : '否') },
    {
      label: '适合人群',
      render: (t) =>
        (t.audiences || []).map((a) => AUDIENCE_LABELS[a] || a).join(' / ') || '—',
    },
    { label: '官方链接', render: (t) => t.official_url || '—', isLink: true },
  ];

  return (
    <div className="pt-6">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-widest text-white/40">Compare</div>
        <h1 className="text-3xl font-black md:text-4xl">多维对比 · 帮你下决定</h1>
      </div>

      <div className="glass overflow-hidden rounded-3xl">
        <div className="grid" style={{ gridTemplateColumns: `10rem repeat(${tools.length}, 1fr)` }}>
          <div className="border-b border-white/5 bg-white/5 p-4 text-xs uppercase text-white/40">
            对比项
          </div>
          {tools.map((t) => (
            <div key={t.id} className="border-b border-white/5 bg-white/5 p-4">
              <Link href={`/tool/${t.slug}`} className="flex items-center gap-3">
                {t.logo_url ? (
                  <img
                    src={t.logo_url}
                    alt={t.name}
                    className="h-10 w-10 rounded-lg bg-white/10 object-contain p-1"
                  />
                ) : (
                  <div className="grid h-10 w-10 place-items-center rounded-lg bg-gradient-to-br from-neon-purple to-neon-blue font-black">
                    {t.name?.[0]}
                  </div>
                )}
                <div className="min-w-0">
                  <div className="truncate text-base font-bold">{t.name}</div>
                  <div className="truncate text-xs text-white/50">{t.tagline || '—'}</div>
                </div>
              </Link>
            </div>
          ))}

          {rows.flatMap((row, idx) => [
            <div
              key={`label-${idx}`}
              className="border-b border-white/5 p-4 text-sm text-white/55"
            >
              {row.label}
            </div>,
            ...tools.map((t) => {
              const val = row.render(t);
              return (
                <div key={`cell-${idx}-${t.id}`} className="border-b border-white/5 p-4">
                  {row.big ? (
                    <div className="text-3xl font-black neon-text">{val}</div>
                  ) : row.isLink && val && val !== '—' ? (
                    <a
                      className="text-neon-cyan hover:underline"
                      href={val}
                      target="_blank"
                      rel="noreferrer"
                    >
                      前往 ↗
                    </a>
                  ) : (
                    <span className="text-sm text-white/85">{val}</span>
                  )}
                </div>
              );
            }),
          ])}
        </div>
      </div>

      <div className="mt-6 text-sm text-white/50">
        还想看别的？去
        <Link href="/" className="ml-1 text-neon-cyan hover:underline">
          首页
        </Link>{' '}
        或{' '}
        <Link href="/search" className="text-neon-cyan hover:underline">
          懂你
        </Link>{' '}
        继续挑 ✨
      </div>
    </div>
  );
}
