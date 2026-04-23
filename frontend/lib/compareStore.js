'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useCompareStore = create(
  persist(
    (set, get) => ({
      ids: [],
      tools: {},
      add: (tool) => {
        const { ids, tools } = get();
        if (ids.includes(tool.id)) return;
        if (ids.length >= 3) return;
        set({ ids: [...ids, tool.id], tools: { ...tools, [tool.id]: tool } });
      },
      remove: (id) => {
        const { ids, tools } = get();
        const nextTools = { ...tools };
        delete nextTools[id];
        set({ ids: ids.filter((i) => i !== id), tools: nextTools });
      },
      clear: () => set({ ids: [], tools: {} }),
      toggle: (tool) => {
        const { ids, add, remove } = get();
        if (ids.includes(tool.id)) remove(tool.id);
        else add(tool);
      },
    }),
    { name: 'trueai-compare' },
  ),
);
