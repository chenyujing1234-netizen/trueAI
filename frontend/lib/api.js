const BASE =
  typeof window === 'undefined'
    ? process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
    : '';

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    cache: 'no-store',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export const api = {
  stats: () => request('/api/stats'),
  categories: () => request('/api/categories'),
  tools: (params = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') qs.append(k, v);
    });
    return request(`/api/tools?${qs.toString()}`);
  },
  tool: (idOrSlug) => request(`/api/tools/${idOrSlug}`),
  rankings: (params = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') qs.append(k, v);
    });
    return request(`/api/rankings?${qs.toString()}`);
  },
  compare: (ids) =>
    request('/api/tools/compare', { method: 'POST', body: JSON.stringify(ids) }),
  reviews: (toolId) => request(`/api/reviews?tool_id=${toolId}`),
  searchQuick: (q) =>
    request(`/api/search/chat?q=${encodeURIComponent(q)}`),
};

export const chatStreamUrl = () => `/api/search/chat`;
