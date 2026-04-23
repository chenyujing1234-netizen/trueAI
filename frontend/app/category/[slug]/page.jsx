import { notFound } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import ToolCard from '@/components/ToolCard';
import FilterBar from '@/components/FilterBar';
import { api } from '@/lib/api';

export const revalidate = 30;

export default async function CategoryPage({ params, searchParams }) {
  const { slug } = params;
  const [categories, list] = await Promise.all([
    api.categories().catch(() => []),
    api
      .tools({
        category: slug,
        sort: searchParams.sort || 'overall',
        form_factor: searchParams.form_factor,
        audience: searchParams.audience,
        free: searchParams.free,
        need_vpn: searchParams.need_vpn,
        page: searchParams.page || 1,
        page_size: 24,
      })
      .catch(() => null),
  ]);

  const cat = categories.find((c) => c.slug === slug);
  if (!cat) return notFound();

  return (
    <div className="pt-6">
      <section className="mb-6 flex items-end justify-between">
        <div>
          <div className="text-xs uppercase tracking-widest text-white/40">Category</div>
          <h1 className="text-3xl font-black md:text-4xl">
            <span className="mr-2">{cat.icon}</span>
            <span className="neon-text">{cat.name}</span>
          </h1>
          <p className="mt-1 text-sm text-white/60">
            共收录 {cat.tool_count} 个 AI 工具 · 经人工筛选，按你选择的维度排序
          </p>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-[14rem_1fr]">
        <Sidebar categories={categories} activeSlug={slug} />
        <div className="min-w-0">
          <FilterBar basePath={`/category/${slug}`} />
          {list && list.items && list.items.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {list.items.map((t, i) => (
                <ToolCard key={t.id} tool={t} index={i} />
              ))}
            </div>
          ) : (
            <div className="glass rounded-2xl p-10 text-center text-white/60">
              这个组合的条件暂时没有匹配的工具，换一个筛选试试？
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
