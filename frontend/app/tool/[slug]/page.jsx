import Link from 'next/link';
import { notFound } from 'next/navigation';

import ScoreRadar from '@/components/ScoreRadar';
import AddToCompareButton from '@/components/AddToCompareButton';
import ReviewList from '@/components/ReviewList';
import BilibiliPlayer from '@/components/BilibiliPlayer';
import ExternalReviews from '@/components/ExternalReviews';
import { api } from '@/lib/api';
import { AUDIENCE_LABELS, FORM_FACTOR_LABELS } from '@/lib/labels';

export const revalidate = 30;

export async function generateMetadata({ params }) {
  try {
    const t = await api.tool(params.slug);
    return {
      title: `${t.name} · TrueAI 智能体详情`,
      description: t.tagline || t.description?.slice(0, 140),
    };
  } catch {
    return { title: 'TrueAI 智能体详情' };
  }
}

export default async function ToolDetailPage({ params }) {
  let tool;
  try {
    tool = await api.tool(params.slug);
  } catch {
    return notFound();
  }

  const infoItems = [
    { k: '开发公司', v: tool.developer || '—' },
    {
      k: '上线时间',
      v: tool.launched_at ? new Date(tool.launched_at).toLocaleDateString('zh-CN') : '—',
    },
    { k: '持续迭代', v: tool.is_iterating ? '是' : '否' },
    { k: '用户体量', v: tool.user_count || '—' },
    { k: '应用形态', v: FORM_FACTOR_LABELS[tool.form_factor] || tool.form_factor },
    { k: '收费情况', v: tool.is_free ? '有免费可用' : '付费' },
    { k: '价格', v: tool.pricing_info || '—' },
    { k: '是否需要外网', v: tool.need_vpn ? '需要' : '不需要' },
    { k: '支持 CLI', v: tool.support_cli ? '是' : '否' },
    { k: '支持 API', v: tool.support_api ? '是' : '否' },
    { k: '评测更新', v: tool.reviewed_at ? new Date(tool.reviewed_at).toLocaleDateString('zh-CN') : '—' },
  ];

  return (
    <div className="pt-6">
      <div className="mb-4 text-sm text-white/50">
        <Link href="/" className="hover:text-white">
          首页
        </Link>
        {' / '}
        {(tool.categories || []).slice(0, 1).map((c) => (
          <Link key={c} href={`/category/${c}`} className="hover:text-white">
            {c}
          </Link>
        ))}
        {' / '}
        <span className="text-white/80">{tool.name}</span>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[20rem_1fr]">
        {/* 左列 */}
        <aside className="glass sticky top-20 flex h-fit flex-col items-center gap-4 rounded-3xl p-6 text-center">
          {tool.logo_url ? (
            <img
              src={tool.logo_url}
              alt={tool.name}
              className="h-24 w-24 rounded-2xl bg-white/10 object-contain p-2"
            />
          ) : (
            <div className="grid h-24 w-24 place-items-center rounded-2xl bg-gradient-to-br from-neon-purple to-neon-blue text-3xl font-black">
              {tool.name?.[0]}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-black">{tool.name}</h1>
            {tool.tagline && <p className="mt-1 text-sm text-white/60">{tool.tagline}</p>}
          </div>

          <div className="w-full rounded-2xl bg-ink-900/70 p-4">
            <div className="text-5xl font-black leading-none neon-text tabular-nums">
              {Number(tool.overall_score || 0).toFixed(1)}
            </div>
            <div className="mt-1 text-xs text-white/50">综合评分 · 满分 10</div>
          </div>

          <div className="flex flex-wrap justify-center gap-1.5">
            {tool.is_free && <span className="chip text-neon-lime">免费</span>}
            {tool.need_vpn ? (
              <span className="chip text-neon-purple">需魔法</span>
            ) : (
              <span className="chip text-neon-cyan">国内直连</span>
            )}
            {tool.support_cli && <span className="chip">CLI</span>}
            {tool.support_api && <span className="chip">API</span>}
          </div>

          <div className="flex w-full flex-col gap-2">
            {tool.official_url && (
              <a
                href={tool.official_url}
                target="_blank"
                rel="noreferrer"
                className="btn-primary w-full"
              >
                前往官方 ↗
              </a>
            )}
            <AddToCompareButton tool={tool} className="w-full" />
          </div>
        </aside>

        {/* 右列 */}
        <div className="flex min-w-0 flex-col gap-8">
          <section className="glass rounded-3xl p-6">
            <h2 className="mb-4 text-lg font-bold">核心评分</h2>
            <ScoreRadar tool={tool} />
          </section>

          <section className="glass rounded-3xl p-6">
            <h2 className="mb-4 text-lg font-bold">基础信息</h2>
            <dl className="grid grid-cols-1 gap-x-8 gap-y-3 sm:grid-cols-2">
              {infoItems.map((i) => (
                <div key={i.k} className="flex items-baseline justify-between border-b border-white/5 pb-2">
                  <dt className="text-sm text-white/55">{i.k}</dt>
                  <dd className="text-sm text-white/90">{i.v}</dd>
                </div>
              ))}
            </dl>
          </section>

          {tool.description && (
            <section className="glass rounded-3xl p-6">
              <h2 className="mb-3 text-lg font-bold">关于 {tool.name}</h2>
              <p className="whitespace-pre-wrap leading-relaxed text-white/80">
                {tool.description}
              </p>
            </section>
          )}

          <BilibiliPlayer videoUrl={tool.video_url} title={`${tool.name} 介绍视频`} />

          <ExternalReviews toolSlug={params.slug} />

          <section className="glass rounded-3xl p-6">
            <h2 className="mb-3 text-lg font-bold">适合人群</h2>
            <div className="flex flex-wrap gap-2">
              {(tool.audiences || []).length ? (
                tool.audiences.map((a) => (
                  <span
                    key={a}
                    className="rounded-full bg-gradient-to-r from-neon-purple/30 to-neon-blue/20 px-3 py-1 text-sm"
                  >
                    {AUDIENCE_LABELS[a] || a}
                  </span>
                ))
              ) : (
                <span className="text-sm text-white/50">编辑部尚未标注，欢迎评测时补充 ✨</span>
              )}
            </div>
          </section>

          <section>
            <div className="mb-4 flex items-end justify-between">
              <h2 className="text-lg font-bold">真实评测</h2>
              <Link href="/earn" className="text-sm text-neon-lime hover:text-white">
                写评测赚钱 →
              </Link>
            </div>
            <ReviewList toolId={tool.id} />
          </section>
        </div>
      </div>
    </div>
  );
}
