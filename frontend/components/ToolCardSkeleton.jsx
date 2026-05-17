export default function ToolCardSkeleton({ hangeffect = false }) {
  return (
    <div className="flex flex-col items-stretch">
      {hangeffect && (
        <div className="mx-auto h-8 flex justify-center">
          <div className="rope opacity-30" />
        </div>
      )}
      <div className="glass rounded-2xl p-4 animate-pulse">
        {/* 顶部：logo + 名称 + 分数 */}
        <div className="flex items-start gap-3 mb-3">
          <div className="h-10 w-10 rounded-xl bg-white/10 shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex justify-between gap-2">
              <div className="h-4 w-24 rounded bg-white/10" />
              <div className="h-6 w-10 rounded bg-white/10" />
            </div>
            <div className="mt-2 h-3 w-full rounded bg-white/8" />
            <div className="mt-1 h-3 w-3/4 rounded bg-white/8" />
          </div>
        </div>
        {/* 标签 */}
        <div className="flex gap-1.5 mb-3">
          <div className="h-5 w-12 rounded-full bg-white/8" />
          <div className="h-5 w-16 rounded-full bg-white/8" />
          <div className="h-5 w-14 rounded-full bg-white/8" />
        </div>
        {/* 底部 */}
        <div className="flex justify-between border-t border-white/5 pt-2">
          <div className="h-3 w-20 rounded bg-white/8" />
          <div className="h-5 w-16 rounded-full bg-white/8" />
        </div>
      </div>
    </div>
  );
}

export function ToolGridSkeleton({ count = 9, hangeffect = false }) {
  return (
    <div className={`grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2 lg:grid-cols-3`}>
      {Array.from({ length: count }).map((_, i) => (
        <ToolCardSkeleton key={i} hangeffect={hangeffect} />
      ))}
    </div>
  );
}
