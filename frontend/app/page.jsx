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

        {/* 开源 / 接入 */}
        <OpenSourceSection />
      </div>
    </div>
  );
}

const REPO_URL = 'https://github.com/chenyujing1234-netizen/trueAI';
const STRUCTAIWEB_URL = 'https://github.com/chenyujing1234-netizen/StructAIWeb';

const ACCESS_POINTS = [
  {
    title: 'GitHub 源码',
    desc: '完整前端 + 后端 + 1600+ 应用数据脚本，欢迎 Star / Fork / PR。',
    href: REPO_URL,
    badge: 'MIT License',
    accent: 'text-neon-cyan',
  },
  {
    title: 'MCP Server',
    desc: '让 Claude、Cursor、Cline 等 Agent 直接拥有「挑 AI 工具」的能力。',
    href: 'https://www.shiflowai.cloud/mcp',
    badge: 'Streamable HTTP',
    accent: 'text-neon-lime',
    sub: '{ "url": "https://www.shiflowai.cloud/mcp" }',
  },
  {
    title: 'Agent Skill',
    desc: '不支持 MCP 的 Agent 也能用——单文件 SKILL.md 直接 drop-in。',
    href: `${REPO_URL}/blob/main/skills/trueai/SKILL.md`,
    badge: 'SKILL.md',
    accent: 'text-neon-pink',
  },
  {
    title: '数据 Schema',
    desc: '每个 AI 应用的 34 个结构化字段（评分 / 价格 / 形态 / 评论 …），JSON Schema 规范。',
    href: `${REPO_URL}/blob/main/docs/ai_tool_schema.json`,
    badge: 'JSON Schema',
    accent: 'text-neon-cyan',
  },
];

function OpenSourceSection() {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/5 bg-ink-900/60 p-8 md:p-10">
      <div className="absolute inset-0 -z-10 bg-aurora opacity-60" />

      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-xs uppercase tracking-widest text-white/40">
            Open Source · Built in the open
          </div>
          <h2 className="mt-1 text-2xl font-black md:text-3xl">
            完全开源 · <span className="neon-text">代码全在 GitHub</span>
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-white/70">
            真选AI 是一个 <strong className="text-white">完全开源</strong> 的项目（MIT 许可），由两个仓库组成：
            <a
              href={REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mx-1 text-neon-cyan hover:underline"
            >
              trueAI
            </a>
            （网站前后端 + 数据 schema + MCP Server）和
            <a
              href={STRUCTAIWEB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mx-1 text-neon-cyan hover:underline"
            >
              StructAIWeb
            </a>
            （驱动数据采集的 AI 智能体）。我们相信「AI 工具的选择权」应该属于用户而不是某个广告系统，
            所以代码、数据、评分逻辑都欢迎你审视、复用、贡献。
          </p>
        </div>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary inline-flex shrink-0 items-center gap-2 px-5 py-3 text-sm font-semibold shadow-glow"
        >
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
            <path d="M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.16c-3.2.7-3.88-1.37-3.88-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.71.08-.71 1.16.08 1.78 1.2 1.78 1.2 1.04 1.79 2.72 1.27 3.39.97.1-.75.41-1.27.74-1.56-2.55-.29-5.24-1.28-5.24-5.71 0-1.26.45-2.29 1.2-3.1-.12-.3-.52-1.49.11-3.11 0 0 .97-.31 3.18 1.18a11.04 11.04 0 0 1 5.79 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.62.23 2.81.11 3.11.75.81 1.2 1.84 1.2 3.1 0 4.44-2.7 5.42-5.27 5.7.42.36.79 1.08.79 2.18v3.23c0 .31.21.68.8.56C20.21 21.39 23.5 17.07 23.5 12 23.5 5.73 18.27.5 12 .5z" />
          </svg>
          <span>在 GitHub 上查看</span>
          <span className="text-white/60">→</span>
        </a>
      </div>

      {/* 核心采集器：StructAIWeb 高亮横幅 */}
      <a
        href={STRUCTAIWEB_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="group mb-6 block overflow-hidden rounded-2xl border border-neon-cyan/30 bg-gradient-to-br from-neon-cyan/[0.08] via-white/[0.04] to-neon-purple/[0.08] p-5 transition hover:border-neon-cyan/60 hover:from-neon-cyan/[0.14]"
      >
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="min-w-0 flex-1">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-neon-cyan/40 bg-neon-cyan/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-neon-cyan">
                Core Agent · 数据来源
              </span>
              <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wider text-white/50">
                Python · Playwright · 多模态视觉
              </span>
            </div>
            <h3 className="text-lg font-black md:text-xl">
              本站 1600+ 应用数据，来自开源智能体{' '}
              <span className="neon-text">StructAIWeb</span>
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-white/70">
              真选AI 的核心评分与结构化字段（名称、定价、子功能、易用性 / 效果 / 性价比 …
              共 34 个字段）<strong className="text-white">不是人工录入</strong>，而是由我们另一个开源项目
              <strong className="text-white"> StructAIWeb </strong>
              自动跑出来的：它接管你本地 Chrome，按"价格 → 功能 → 关于 → 文档"启发式探索任意 AI SaaS 网站，
              点 CTA 主动试用（永远避开付费按钮），再用 LLM + 多模态视觉模型整合成客观可比的结构化报告。
              <strong className="text-white">想自己跑数据 / 扩展到更多 AI 工具？fork 即可。</strong>
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2 rounded-xl border border-neon-cyan/30 bg-ink-950/40 px-4 py-3 text-sm font-semibold text-neon-cyan group-hover:border-neon-cyan group-hover:bg-neon-cyan/10">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
              <path d="M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.16c-3.2.7-3.88-1.37-3.88-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.71.08-.71 1.16.08 1.78 1.2 1.78 1.2 1.04 1.79 2.72 1.27 3.39.97.1-.75.41-1.27.74-1.56-2.55-.29-5.24-1.28-5.24-5.71 0-1.26.45-2.29 1.2-3.1-.12-.3-.52-1.49.11-3.11 0 0 .97-.31 3.18 1.18a11.04 11.04 0 0 1 5.79 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.62.23 2.81.11 3.11.75.81 1.2 1.84 1.2 3.1 0 4.44-2.7 5.42-5.27 5.7.42.36.79 1.08.79 2.18v3.23c0 .31.21.68.8.56C20.21 21.39 23.5 17.07 23.5 12 23.5 5.73 18.27.5 12 .5z" />
            </svg>
            <span>查看 StructAIWeb</span>
            <span className="text-white/50">↗</span>
          </div>
        </div>
      </a>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {ACCESS_POINTS.map((it) => (
          <a
            key={it.title}
            href={it.href}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-white/30 hover:bg-white/[0.07]"
          >
            <div className="flex items-center justify-between">
              <h3 className={`text-base font-bold ${it.accent}`}>{it.title}</h3>
              <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wider text-white/50">
                {it.badge}
              </span>
            </div>
            <p className="text-xs leading-relaxed text-white/65">{it.desc}</p>
            {it.sub ? (
              <code className="rounded-md bg-black/40 px-2 py-1 text-[11px] text-neon-lime/90">
                {it.sub}
              </code>
            ) : null}
            <div className="mt-auto text-xs text-white/40 group-hover:text-white">
              打开 →
            </div>
          </a>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-white/40">
        <span>觉得有用？</span>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-white/70 underline-offset-2 hover:text-white hover:underline"
        >
          点个 Star
        </a>
        <span>·</span>
        <a
          href={`${REPO_URL}/issues/new`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-white/70 underline-offset-2 hover:text-white hover:underline"
        >
          提建议 / Bug
        </a>
        <span>·</span>
        <a
          href={`${REPO_URL}/pulls`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-white/70 underline-offset-2 hover:text-white hover:underline"
        >
          贡献代码（PR）
        </a>
      </div>
    </section>
  );
}
