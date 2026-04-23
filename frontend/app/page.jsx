import Link from 'next/link';
import HeroTypewriter from '@/components/HeroTypewriter';
import StatsBar from '@/components/StatsBar';
import Sidebar from '@/components/Sidebar';
import ToolCard from '@/components/ToolCard';
import HomeSearchBox from '@/components/HomeSearchBox';
import { api } from '@/lib/api';

export const revalidate = 30;

async function safeFetch(promise, fallback) {
  try {
    return await promise;
  } catch (e) {
    console.error('[home] fetch error', e?.message);
    return fallback;
  }
}

export default async function HomePage() {
  const [stats, categories, top, newest] = await Promise.all([
    safeFetch(api.stats(), { tools: 0, categories: 0, reviews: 0, users: 0 }),
    safeFetch(api.categories(), []),
    safeFetch(api.tools({ sort: 'overall', page_size: 9 }), { items: [] }),
    safeFetch(api.tools({ sort: 'new', page_size: 6 }), { items: [] }),
  ]);

  return (
    <div className="pt-6">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-white/5 bg-ink-900/60 p-8 md:p-14">
        <div className="absolute inset-0 -z-10 bg-aurora opacity-90" />
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
          <span className="h-1.5 w-1.5 rounded-full bg-neon-cyan" />
          新一代 AI 导航 · 懂你版
        </div>
        <h1 className="text-3xl font-black leading-tight md:text-5xl">
          真选<span className="neon-text">AI</span>
          <span className="text-white/60"> — </span>
          <HeroTypewriter />
        </h1>
        <p className="mt-4 max-w-2xl text-white/70">
          AI 工具太多，选择成本太大？告诉我你的真实场景，我们的"懂你"助手会用对话的方式，
          结合实时人工评测，推荐最适合你的那一个。数据实时 · 人工评测 · 无广告 · 你评测我付钱。
        </p>
        <div className="mt-6">
          <HomeSearchBox />
        </div>
        <div className="mt-6">
          <StatsBar stats={stats} />
        </div>
      </section>

      {/* 主体三栏：侧栏 + 卡片墙 */}
      <section className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-[14rem_1fr]">
        <Sidebar categories={categories} />
        <div className="flex min-w-0 flex-col gap-10">
          <div>
            <div className="mb-5 flex items-end justify-between">
              <div>
                <div className="text-xs uppercase tracking-widest text-white/40">
                  Editor's Picks
                </div>
                <h2 className="text-2xl font-black">
                  今日推荐 · <span className="neon-text">综合评分 TOP</span>
                </h2>
              </div>
              <Link href="/rankings" className="text-sm text-white/60 hover:text-white">
                查看完整排行榜 →
              </Link>
            </div>
            <div className="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
              {(top.items || []).map((t, i) => (
                <ToolCard key={t.id} tool={t} index={i} hangeffect />
              ))}
            </div>
          </div>

          <div>
            <div className="mb-5 flex items-end justify-between">
              <div>
                <div className="text-xs uppercase tracking-widest text-white/40">Just Added</div>
                <h2 className="text-2xl font-black">
                  新入库 · <span className="neon-text">等你来评测</span>
                </h2>
              </div>
              <Link
                href="/earn"
                className="text-sm text-neon-lime hover:text-white"
                title="去领取评测任务赚钱"
              >
                我要评测赚钱 →
              </Link>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {(newest.items || []).map((t, i) => (
                <ToolCard key={t.id} tool={t} index={i} />
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
