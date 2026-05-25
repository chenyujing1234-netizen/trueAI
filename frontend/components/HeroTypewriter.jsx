'use client';

import { useEffect, useState } from 'react';

const DEFAULT_LINES = [
  '帮你快速找到最合适你的AI工具',
];

export default function HeroTypewriter({ lines = DEFAULT_LINES, speed = 65, pause = 1500 }) {
  const [idx, setIdx] = useState(0);
  const [text, setText] = useState('');
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const full = lines[idx % lines.length];
    let t;
    if (!deleting && text.length < full.length) {
      t = setTimeout(() => setText(full.slice(0, text.length + 1)), speed);
    } else if (!deleting && text.length === full.length) {
      t = setTimeout(() => setDeleting(true), pause);
    } else if (deleting && text.length > 0) {
      t = setTimeout(() => setText(full.slice(0, text.length - 1)), speed / 2);
    } else if (deleting && text.length === 0) {
      setDeleting(false);
      setIdx((i) => (i + 1) % lines.length);
    }
    return () => clearTimeout(t);
  }, [text, deleting, idx, lines, speed, pause]);

  return (
    <span className="inline-flex items-baseline">
      <span className="neon-text">{text}</span>
      <span className="ml-1 inline-block h-[0.9em] w-[3px] translate-y-[2px] bg-neon-cyan animate-blink" />
    </span>
  );
}
