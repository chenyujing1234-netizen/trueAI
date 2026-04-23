import ChatSearch from '@/components/ChatSearch';

export const metadata = { title: '懂你 · 对话式 AI 导航 — TrueAI' };

export default function SearchPage({ searchParams }) {
  const q = searchParams?.q || '';
  return (
    <div className="pt-6">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-widest text-white/40">Conversational Search</div>
        <h1 className="text-3xl font-black md:text-4xl">
          <span className="neon-text">懂你</span> · 告诉我你要做什么，我帮你挑
        </h1>
        <p className="mt-2 text-sm text-white/60">
          比起让你描述清楚需求，不如让 AI 反问你几个关键问题。先从本站评测库召回，再由"懂你"排序解释。
          若库内没有完全匹配，我们会把你导航到其他更全的 AI 目录。
        </p>
      </div>
      <ChatSearch initialQuery={q} />
    </div>
  );
}
