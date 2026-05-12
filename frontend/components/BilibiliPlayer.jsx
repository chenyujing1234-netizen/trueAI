'use client';

export default function BilibiliPlayer({ videoUrl, title }) {
  const bvid = extractBvid(videoUrl);
  if (!bvid) return null;

  const embedUrl = `https://player.bilibili.com/player.html?bvid=${bvid}&autoplay=0&danmaku=0`;

  return (
    <section className="glass rounded-3xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold">视频介绍</h2>
        <a
          href={`https://www.bilibili.com/video/${bvid}`}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 text-xs text-white/50 hover:text-neon-cyan transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L8.38 4.679c.267.249.4.556.4.906v.026h4.16V5.56c0-.35.133-.657.4-.906l1.56-1.48c.267-.249.573-.373.92-.373.347 0 .653.124.92.373.267.249.4.556.4.906 0 .355-.133.657-.4.906l-1.12 1.066zM9.6 14.173a.8.8 0 1 0 0-1.6.8.8 0 0 0 0 1.6zm4.8 0a.8.8 0 1 0 0-1.6.8.8 0 0 0 0 1.6z"/>
          </svg>
          在 B 站观看
        </a>
      </div>
      <div className="relative w-full overflow-hidden rounded-2xl bg-black/40" style={{ paddingTop: '56.25%' }}>
        <iframe
          src={embedUrl}
          title={title || '视频介绍'}
          className="absolute inset-0 h-full w-full border-0"
          allowFullScreen
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          sandbox="allow-same-origin allow-scripts allow-popups allow-presentation"
        />
      </div>
    </section>
  );
}

function extractBvid(url) {
  if (!url) return null;
  // 直接是 BVid 格式
  if (/^BV[a-zA-Z0-9]+$/.test(url)) return url;
  // 从 URL 中提取
  const m = url.match(/\/video\/(BV[a-zA-Z0-9]+)/);
  return m ? m[1] : null;
}
