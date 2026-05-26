/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [{ protocol: 'https', hostname: '**' }],
  },
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';
    return [
      { source: '/api/:path*',                destination: `${api}/api/:path*` },
      { source: '/mcp',                       destination: `${api}/mcp` },
      { source: '/mcp/:path*',                destination: `${api}/mcp/:path*` },
      { source: '/mcp-sse/:path*',            destination: `${api}/mcp-sse/:path*` },
      { source: '/.well-known/mcp/:path*',    destination: `${api}/.well-known/mcp/:path*` },
    ];
  },
};

module.exports = nextConfig;
