export const metadata = { title: '我要赚钱 · TrueAI' };

export default function EarnPage() {
  return (
    <div className="mx-auto mt-10 max-w-3xl">
      <div className="glass rounded-3xl p-8">
        <div className="text-xs uppercase tracking-widest text-white/40">Earn with TrueAI</div>
        <h1 className="mt-2 text-4xl font-black">
          <span className="neon-text">你评测，我付钱。</span>
        </h1>
        <p className="mt-3 text-white/70">
          官方会持续发布"某个 AI 是否真的好用"的评测任务。你领取任务、真实体验、撰写评测，
          经过审核通过后即可获得奖励，可直接打到你的微信账户。
        </p>
        <div className="mt-6 rounded-2xl border border-dashed border-white/15 p-6 text-white/70">
          <div className="text-sm">任务系统 MVP 开发中，敬请期待 ✨</div>
          <div className="mt-1 text-xs text-white/40">
            提示：计划中的数据库表已预留，后续版本会开放。
          </div>
        </div>
      </div>
    </div>
  );
}
