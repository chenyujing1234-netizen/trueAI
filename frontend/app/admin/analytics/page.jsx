'use client';

import { useEffect, useState, useCallback } from 'react';

const API =
  typeof window === 'undefined'
    ? process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
    : '';

async function fetchJSON(path) {
  const r = await fetch(`${API}${path}`, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

// ─── 小组件 ─────────────────────────────────

function StatCard({ label, value, sub, accent = false }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="text-xs text-white/50 mb-1">{label}</div>
      <div className={`text-3xl font-black tabular-nums ${accent ? 'neon-text' : 'text-white'}`}>
        {value ?? '—'}
      </div>
      {sub && <div className="mt-1 text-xs text-white/40">{sub}</div>}
    </div>
  );
}

function SectionTitle({ children }) {
  return <h2 className="text-sm font-bold text-white/60 uppercase tracking-widest mb-3">{children}</h2>;
}

// ─── 迷你折线图（纯 SVG，无依赖）─────────────────

function Sparkline({ data, color = '#00f0ff', height = 60 }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data, 1);
  const w = 400;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = height - (v / max) * (height - 4) - 2;
    return `${x},${y}`;
  });
  const area = `M0,${height} L${pts.join(' L')} L${w},${height} Z`;
  const line = `M${pts.join(' L')}`;
  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" style={{ height }}>
      <defs>
        <linearGradient id={`grad-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#grad-${color.replace('#', '')})`} />
      <path d={line} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" />
    </svg>
  );
}

// ─── 每小时柱状图 ────────────────────────────

function HourlyBar({ data }) {
  if (!data) return null;
  const max = Math.max(...data.map((d) => d.pv), 1);
  return (
    <div className="flex items-end gap-0.5 h-16 w-full">
      {data.map((d) => (
        <div key={d.hour} className="flex-1 flex flex-col items-center gap-0.5 group">
          <div
            className="w-full rounded-t bg-neon-cyan/60 group-hover:bg-neon-cyan transition-all"
            style={{ height: `${Math.max((d.pv / max) * 52, d.pv > 0 ? 3 : 0)}px` }}
            title={`${d.hour}:00  ${d.pv} 次`}
          />
        </div>
      ))}
    </div>
  );
}

// ─── 主页面 ─────────────────────────────────

export default function AnalyticsPage() {
  const [summary,   setSummary]   = useState(null);
  const [daily,     setDaily]     = useState([]);
  const [topPages,  setTopPages]  = useState([]);
  const [topIps,    setTopIps]    = useState([]);
  const [recent,    setRecent]    = useState([]);
  const [hourly,    setHourly]    = useState([]);
  const [days,      setDays]      = useState(30);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);
  const [tab,       setTab]       = useState('overview');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, d, tp, ti, r, h] = await Promise.all([
        fetchJSON('/api/analytics/summary'),
        fetchJSON(`/api/analytics/daily?days=${days}`),
        fetchJSON(`/api/analytics/top-pages?days=${days}&limit=20`),
        fetchJSON(`/api/analytics/top-ips?days=${days}&limit=20`),
        fetchJSON('/api/analytics/recent?limit=50'),
        fetchJSON('/api/analytics/hourly?days=1'),
      ]);
      setSummary(s);
      setDaily(d);
      setTopPages(tp);
      setTopIps(ti);
      setRecent(r);
      setHourly(h);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => { load(); }, [load]);

  // 自动刷新（60 秒）
  useEffect(() => {
    const t = setInterval(load, 60_000);
    return () => clearInterval(t);
  }, [load]);

  const pvList  = daily.map((d) => d.pv);
  const uvList  = daily.map((d) => d.uv);
  const dateLabels = daily.length ? [daily[0]?.date, daily[daily.length - 1]?.date] : [];

  return (
    <div className="pt-8 pb-24 space-y-8">
      {/* 标题栏 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black">访问数据看板</h1>
          <p className="text-sm text-white/50 mt-0.5">实时记录用户访问 IP、路径、行为</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="glass rounded-xl px-3 py-2 text-sm text-white/80 bg-transparent cursor-pointer"
          >
            {[7, 14, 30, 60, 90].map((n) => (
              <option key={n} value={n} className="bg-gray-900">{n} 天</option>
            ))}
          </select>
          <button
            onClick={load}
            className="btn-ghost h-9 px-4 text-sm"
            disabled={loading}
          >
            {loading ? '加载中…' : '刷新'}
          </button>
        </div>
      </div>

      {error && (
        <div className="glass rounded-2xl p-4 text-neon-pink text-sm">
          加载失败：{error}。请确认后端服务正在运行。
        </div>
      )}

      {/* 汇总卡片 */}
      {summary && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="今日 PV" value={summary.today.pv.toLocaleString()} accent />
          <StatCard label="今日 UV（独立访客）" value={summary.today.uv.toLocaleString()} />
          <StatCard
            label="昨日 PV"
            value={summary.yesterday.pv.toLocaleString()}
            sub={`昨日 UV：${summary.yesterday.uv}`}
          />
          <StatCard
            label="累计 PV"
            value={summary.total.pv.toLocaleString()}
            sub={`累计 UV：${summary.total.uv}`}
          />
        </div>
      )}

      {/* 标签页 */}
      <div className="flex gap-2 border-b border-white/10 pb-0">
        {[
          { key: 'overview', label: '流量趋势' },
          { key: 'pages',    label: '热门页面' },
          { key: 'ips',      label: 'IP 分析' },
          { key: 'realtime', label: '实时日志' },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t.key
                ? 'border-neon-cyan text-neon-cyan'
                : 'border-transparent text-white/50 hover:text-white'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* 流量趋势 */}
      {tab === 'overview' && (
        <div className="space-y-6">
          <div className="glass rounded-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <SectionTitle>PV 趋势（近 {days} 天）</SectionTitle>
              {dateLabels.length === 2 && (
                <span className="text-xs text-white/40">{dateLabels[0]} → {dateLabels[1]}</span>
              )}
            </div>
            <Sparkline data={pvList} color="#00f0ff" height={80} />
            <div className="mt-3 flex gap-6 text-xs text-white/40">
              <span>峰值：{Math.max(...pvList, 0)} PV</span>
              <span>均值：{pvList.length ? Math.round(pvList.reduce((a, b) => a + b, 0) / pvList.length) : 0} PV/天</span>
            </div>
          </div>

          <div className="glass rounded-3xl p-6">
            <SectionTitle>UV 趋势（独立访客，近 {days} 天）</SectionTitle>
            <Sparkline data={uvList} color="#b36bff" height={80} />
          </div>

          <div className="glass rounded-3xl p-6">
            <SectionTitle>今日 24 小时 PV 分布</SectionTitle>
            <HourlyBar data={hourly} />
            <div className="flex justify-between text-xs text-white/30 mt-1 px-0.5">
              <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>23:00</span>
            </div>
          </div>

          <div className="glass rounded-3xl p-6">
            <SectionTitle>平均响应时间</SectionTitle>
            <div className="text-4xl font-black tabular-nums">
              <span className={summary?.avg_response_ms > 500 ? 'text-neon-pink' : 'neon-text'}>
                {summary?.avg_response_ms ?? '—'}
              </span>
              <span className="text-sm font-normal text-white/40 ml-1">ms</span>
            </div>
            <p className="text-xs text-white/40 mt-1">所有接口的平均响应耗时（越低越好）</p>
          </div>
        </div>
      )}

      {/* 热门页面 */}
      {tab === 'pages' && (
        <div className="glass rounded-3xl p-6">
          <SectionTitle>热门路径（近 {days} 天，前 20）</SectionTitle>
          <div className="space-y-2 mt-2">
            {topPages.length === 0 && (
              <p className="text-white/40 text-sm">暂无数据</p>
            )}
            {topPages.map((p, i) => {
              const maxPv = topPages[0]?.pv || 1;
              return (
                <div key={p.path} className="flex items-center gap-3">
                  <span className="text-xs text-white/30 w-5 text-right">{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-sm truncate text-white/90">{p.path}</span>
                      <span className="text-xs text-white/50 shrink-0 ml-2">
                        {p.pv.toLocaleString()} PV · {p.uv} UV
                      </span>
                    </div>
                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-neon-cyan/60 rounded-full"
                        style={{ width: `${(p.pv / maxPv) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* IP 分析 */}
      {tab === 'ips' && (
        <div className="glass rounded-3xl p-6">
          <SectionTitle>高频访问 IP（近 {days} 天，前 20）</SectionTitle>
          <p className="text-xs text-white/40 mb-4">访问量异常高的 IP 可能是爬虫或机器人</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-white/40 text-xs">
                  <th className="text-left pb-2">IP 地址</th>
                  <th className="text-right pb-2">PV</th>
                  <th className="text-right pb-2">访问页面数</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {topIps.length === 0 && (
                  <tr><td colSpan={3} className="py-4 text-white/40">暂无数据</td></tr>
                )}
                {topIps.map((row) => (
                  <tr key={row.ip}>
                    <td className="py-2 font-mono text-neon-cyan/80">{row.ip}</td>
                    <td className="py-2 text-right tabular-nums">{row.pv.toLocaleString()}</td>
                    <td className="py-2 text-right tabular-nums text-white/50">{row.pages}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 实时日志 */}
      {tab === 'realtime' && (
        <div className="glass rounded-3xl p-6">
          <SectionTitle>最近 50 条访问记录</SectionTitle>
          <div className="overflow-x-auto mt-2">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-white/40">
                  <th className="text-left pb-2 pr-4">时间</th>
                  <th className="text-left pb-2 pr-4">IP</th>
                  <th className="text-left pb-2 pr-4">方法</th>
                  <th className="text-left pb-2 pr-4">路径</th>
                  <th className="text-right pb-2 pr-4">状态</th>
                  <th className="text-right pb-2">耗时</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {recent.length === 0 && (
                  <tr><td colSpan={6} className="py-4 text-white/40">暂无记录</td></tr>
                )}
                {recent.map((r) => (
                  <tr key={r.id} className="hover:bg-white/3 transition-colors">
                    <td className="py-1.5 pr-4 text-white/40 whitespace-nowrap font-mono">
                      {new Date(r.created_at).toLocaleString('zh-CN', { hour12: false })}
                    </td>
                    <td className="py-1.5 pr-4 font-mono text-neon-cyan/70">{r.ip}</td>
                    <td className="py-1.5 pr-4 text-white/60">{r.method}</td>
                    <td className="py-1.5 pr-4 text-white/80 max-w-[260px] truncate">{r.path}</td>
                    <td className={`py-1.5 pr-4 text-right font-mono ${
                      r.status_code >= 500 ? 'text-neon-pink' :
                      r.status_code >= 400 ? 'text-yellow-400' : 'text-neon-lime'
                    }`}>
                      {r.status_code}
                    </td>
                    <td className="py-1.5 text-right tabular-nums text-white/40">
                      {r.response_time_ms != null ? `${r.response_time_ms}ms` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
