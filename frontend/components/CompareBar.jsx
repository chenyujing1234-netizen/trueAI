'use client';

import Link from 'next/link';
import { AnimatePresence, motion } from 'framer-motion';
import { useCompareStore } from '@/lib/compareStore';

export default function CompareBar() {
  const ids = useCompareStore((s) => s.ids);
  const tools = useCompareStore((s) => s.tools);
  const remove = useCompareStore((s) => s.remove);
  const clear = useCompareStore((s) => s.clear);

  return (
    <AnimatePresence>
      {ids.length > 0 && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          className="fixed bottom-4 left-4 right-4 z-50 mx-auto max-w-[920px]"
        >
          <div className="glass rounded-2xl px-4 py-3 shadow-glow">
            <div className="flex items-center gap-3">
              <div className="shrink-0 text-xs text-white/60">
                已选 <span className="text-neon-cyan font-bold">{ids.length}</span>/3
              </div>

              <div className="flex min-w-0 flex-1 flex-wrap gap-2">
                {ids.map((id) => {
                  const t = tools[id];
                  return (
                    <div
                      key={id}
                      className="flex min-w-0 items-center gap-2 rounded-full bg-white/5 px-3 py-1 text-xs"
                    >
                      {t?.logo_url ? (
                        <img src={t.logo_url} alt="" className="h-4 w-4 shrink-0 rounded" />
                      ) : null}
                      <span className="max-w-[10rem] truncate">{t?.name || `#${id}`}</span>
                      <button
                        onClick={() => remove(id)}
                        className="shrink-0 text-white/40 hover:text-neon-pink"
                        aria-label="移除"
                      >
                        ×
                      </button>
                    </div>
                  );
                })}
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <button onClick={clear} className="btn-ghost h-9 px-3 text-xs">
                  清空
                </button>
                <Link
                  href={`/compare?ids=${ids.join(',')}`}
                  className={[
                    'btn-primary h-9 px-4 text-sm whitespace-nowrap',
                    ids.length < 2 ? 'pointer-events-none opacity-40' : '',
                  ].join(' ')}
                >
                  开始对比 →
                </Link>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
