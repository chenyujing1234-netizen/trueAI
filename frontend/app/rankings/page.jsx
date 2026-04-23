import RankingView from '@/components/RankingView';
import { api } from '@/lib/api';

export const metadata = { title: '排行榜 · TrueAI' };
export const revalidate = 30;

export default async function RankingsPage({ searchParams }) {
  const dimension = searchParams?.dimension || 'overall';
  const category = searchParams?.category || '';
  const [categories, data] = await Promise.all([
    api.categories().catch(() => []),
    api.rankings({ dimension, category, top: 12 }).catch(() => ({ items: [] })),
  ]);

  return (
    <div className="pt-6">
      <div className="mb-6">
        <div className="text-xs uppercase tracking-widest text-white/40">Leaderboard</div>
        <h1 className="text-3xl font-black md:text-4xl">
          <span className="neon-text">TrueAI 排行榜</span>
        </h1>
        <p className="mt-2 text-sm text-white/60">
          默认按综合评分排序；切换分类或维度，立即得到专属榜单。想要更个性化的？
          直接在输入框用自然语言描述你的需求，让"懂你"生成。
        </p>
      </div>

      <RankingView
        categories={categories}
        items={data.items || []}
        dimension={dimension}
        category={category}
      />
    </div>
  );
}
