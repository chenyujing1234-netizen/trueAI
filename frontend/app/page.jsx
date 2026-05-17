import { Suspense } from 'react';
import Link from 'next/link';
import HeroTypewriter from '@/components/HeroTypewriter';
import StatsBar from '@/components/StatsBar';
import Sidebar from '@/components/Sidebar';
import ToolCard from '@/components/ToolCard';
import HomeSearchBox from '@/components/HomeSearchBox';
import { ToolGridSkeleton } from '@/components/ToolCardSkeleton';
import { api } from '@/lib/api';

export const revalidate = 30;

// ─── 异步数据子组件：各自独立加载，不互相阻塞 ──────────────

async function TopTools() {
  try {
    const data = await api.tools({ sort: 'overall', page_size: 9 });
    return (
      <div className="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
        {(data.items || []).map((t, i) => (
          <ToolCard key={t.id} tool={t} index={i} hangeffect />
        ))}
      </div>
    );
  } catch {
    return <p className="text-white/40 text-sm">加载失败，请刷新重试</p>;
  }
}

async function NewestTools() {
  try {
    const data = await api.tools({ sort: 'new', page_size: 6 });
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {(data.items || []).map((t, i) => (
          <ToolCard key={t.id} tool={t} index={i} />
        ))}
      </div>
    );
  } catch {
    return <p className="text-white/40 text-sm">加载失败，请刷新重试</p>;
  }
}

async function SidebarData() {
  try {
    const categories = await api.categories();
    return <Sidebar categories={categories} />;
  } catch {
    return <Sidebar categories={[]} />;
  }
}

async function HeroStats() {
  try {
    const stats = await api.stats();
    return <StatsBar stats={stats} />;
  } catch {
    return null;
  }
}

// ─── 主页面（壳子立即渲染，各 section 独立流入）──────────────

export default function HomePage() {
  return (
    <div className="grid grid-cols-1 gap-6 pt-6 md:grid-cols-[14rem_1fr]">
      <Suspense fallback={<div className="hidden md:block" />}>
        <SidebarData />
      </Suspense>

      <div className="flex min-w-0 flex-col gap-10">
        {/* Hero：纯静态，立即显示，无需等待数据 */}
        <section className="relative overflow-hidden rounded-3xl border border-white/5 bg-ink-900/60 p-8 md:p-12">
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
            <Suspense fallback={<div className="h-8" />}>
              <HeroStats />
            </Suspense>
          </div>
        </section>

        {/* 今日推荐：骨架屏先显示，数据到了流式替换 */}
        <section>
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
          <Suspense fallback={<ToolGridSkeleton count={9} hangeffect />}>
            <TopTools />
          </Suspense>
        </section>

        {/* 新入库 */}
        <section>
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
          <Suspense fallback={<ToolGridSkeleton count={6} />}>
            <NewestTools />
          </Suspense>
        </section>
      </div>
    </div>
  );
}
