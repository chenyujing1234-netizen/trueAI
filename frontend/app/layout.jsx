import './globals.css';
import NavBar from '@/components/NavBar';
import CompareBar from '@/components/CompareBar';

export const metadata = {
  title: '真选AI (TrueAI) — 新一代 AI 导航，懂你',
  description:
    '我来帮你省钱、省时间。无广告、实时人工评测的 AI 工具导航与推荐平台。没有最好的，只有最适合你的。',
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body className="bg-aurora min-h-screen">
        <NavBar />
        <main className="mx-auto max-w-[1400px] px-4 pb-24">{children}</main>
        <CompareBar />
      </body>
    </html>
  );
}
