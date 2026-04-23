'use client';

import { useEffect, useRef, useState } from 'react';
import ToolCard from './ToolCard';

const SUGGEST = [
  '我是新手，想学编程，推荐一个免费的 AI 工具',
  '做短视频的文案 + 配图 + 配音，一条龙推荐',
  '要给小孩子用的，不能付费也不能要翻墙',
  '国内能直连的 AI 画图，国风水墨题材',
];

function parseSSE(text, onEvent) {
  // text 可能包含若干条 "event: x\ndata: {...}\n\n"
  const parts = text.split('\n\n');
  for (const p of parts) {
    if (!p.trim()) continue;
    const lines = p.split('\n');
    let event = 'message';
    let data = '';
    for (const l of lines) {
      if (l.startsWith('event:')) event = l.slice(6).trim();
      else if (l.startsWith('data:')) data += l.slice(5).trim();
    }
    try {
      onEvent(event, data ? JSON.parse(data) : {});
    } catch (_) {
      // ignore parse error
    }
  }
}

export default function ChatSearch({ initialQuery = '' }) {
  const [messages, setMessages] = useState([]); // {role, content, candidates?, external?}
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);
  const fired = useRef(false);

  useEffect(() => {
    if (initialQuery && !fired.current) {
      fired.current = true;
      send(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuery]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  async function send(text) {
    if (!text.trim() || loading) return;
    const userMsg = { role: 'user', content: text.trim() };
    const history = [...messages, userMsg];
    setMessages([...history, { role: 'assistant', content: '', candidates: [], external: [] }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/search/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: history.map(({ role, content }) => ({ role, content })),
        }),
      });
      if (!res.ok || !res.body) {
        throw new Error('HTTP ' + res.status);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lastBoundary = buffer.lastIndexOf('\n\n');
        if (lastBoundary === -1) continue;
        const chunk = buffer.slice(0, lastBoundary + 2);
        buffer = buffer.slice(lastBoundary + 2);
        parseSSE(chunk, (event, data) => {
          if (event === 'meta') {
            setMessages((prev) => {
              const copy = [...prev];
              const last = copy[copy.length - 1];
              last.candidates = data.candidates || [];
              last.external = data.external || [];
              last.provider = data.provider;
              return copy;
            });
          } else if (event === 'delta') {
            setMessages((prev) => {
              const copy = [...prev];
              const last = copy[copy.length - 1];
              last.content = (last.content || '') + (data.text || '');
              return copy;
            });
          }
        });
      }
    } catch (e) {
      setMessages((prev) => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        last.content = (last.content || '') + `\n\n【出错啦】${e.message || e}`;
        return copy;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_20rem]">
      <div className="glass flex h-[calc(100vh-18rem)] min-h-[520px] flex-col rounded-3xl">
        <div ref={scrollRef} className="scrollbar-thin flex-1 overflow-y-auto p-5">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="grid h-16 w-16 place-items-center rounded-2xl bg-gradient-to-br from-neon-purple to-neon-blue shadow-glow">
                <span className="text-2xl">✨</span>
              </div>
              <h2 className="mt-4 text-xl font-bold">开始和"懂你"聊聊</h2>
              <p className="mt-2 max-w-md text-sm text-white/60">
                不用把需求讲得完美 —— 说得越具体越好，模糊也没关系，我会反问你。
              </p>
              <div className="mt-5 flex max-w-xl flex-wrap justify-center gap-2 text-xs">
                {SUGGEST.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-white/70 transition hover:border-neon-purple/60 hover:text-white"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={['mb-6 flex gap-3', m.role === 'user' ? 'justify-end' : ''].join(' ')}
            >
              {m.role === 'assistant' && (
                <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue text-sm">
                  ✦
                </div>
              )}
              <div className={['max-w-[80%]', m.role === 'user' ? 'order-last' : ''].join(' ')}>
                <div
                  className={[
                    'whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed',
                    m.role === 'user'
                      ? 'bg-gradient-to-br from-neon-purple/40 to-neon-blue/30 text-white'
                      : 'bg-white/5 text-white/90',
                  ].join(' ')}
                >
                  {m.content || (m.role === 'assistant' ? '思考中…' : '')}
                </div>
                {m.role === 'assistant' && m.candidates && m.candidates.length > 0 && (
                  <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
                    {m.candidates.slice(0, 4).map((t, k) => (
                      <ToolCard key={t.id} tool={t} index={k} />
                    ))}
                  </div>
                )}
                {m.role === 'assistant' && (!m.candidates || m.candidates.length === 0) &&
                  m.external && m.external.length > 0 && (
                    <div className="mt-3 rounded-2xl border border-dashed border-white/15 p-4">
                      <div className="mb-2 text-xs text-white/60">
                        本站暂无完全匹配 · 试试下面这些外部 AI 导航站
                      </div>
                      <ul className="flex flex-col gap-2 text-sm">
                        {m.external.map((e) => (
                          <li key={e.url}>
                            <a
                              className="text-neon-cyan hover:underline"
                              href={e.url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {e.name}
                            </a>
                            <span className="ml-2 text-white/50">{e.desc}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>
              {m.role === 'user' && (
                <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-white/10 text-sm">
                  🙂
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="border-t border-white/5 p-3">
          <div className="flex items-end gap-2 rounded-2xl bg-white/5 p-2">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              placeholder="说说你的真实场景，比如：我要做小红书封面"
              className="max-h-32 flex-1 resize-none bg-transparent px-3 py-2 text-sm text-white placeholder:text-white/40 focus:outline-none"
            />
            <button
              disabled={loading}
              onClick={() => send(input)}
              className="btn-primary h-10 px-5 text-sm disabled:opacity-50"
            >
              {loading ? '思考中…' : '发送'}
            </button>
          </div>
        </div>
      </div>

      <aside className="glass h-fit rounded-3xl p-5">
        <div className="text-xs uppercase tracking-widest text-white/40">How it works</div>
        <h3 className="mt-1 text-lg font-bold">三步帮你选</h3>
        <ol className="mt-3 flex flex-col gap-3 text-sm text-white/75">
          <li>
            <span className="mr-2 rounded-full bg-white/10 px-2 py-0.5 text-xs">1</span>
            先从本站评测库（MySQL）做候选召回
          </li>
          <li>
            <span className="mr-2 rounded-full bg-white/10 px-2 py-0.5 text-xs">2</span>
            如果你的需求含糊，"懂你"会反问一个关键问题
          </li>
          <li>
            <span className="mr-2 rounded-full bg-white/10 px-2 py-0.5 text-xs">3</span>
            最终给 1-3 个推荐，你可以加入对比或直接跳官方
          </li>
        </ol>
        <div className="mt-5 rounded-2xl bg-white/5 p-3 text-xs text-white/60">
          提示：如果 LLM Key 未配置，当前会走 Mock 文案兜底，但候选卡片依然是真实数据。
        </div>
      </aside>
    </div>
  );
}
