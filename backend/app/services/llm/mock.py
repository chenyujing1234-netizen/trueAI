from __future__ import annotations

import asyncio
from typing import AsyncIterator, Iterable

from app.services.llm.base import LLMProvider


class MockLLM(LLMProvider):
    """没有 API Key 时的回退实现：按照用户最近一条消息返回示例文案，按字吐字模拟流式。"""

    name = "mock"

    async def stream_chat(self, messages: Iterable[dict]) -> AsyncIterator[str]:
        msgs = list(messages)
        last_user = next((m["content"] for m in reversed(msgs) if m.get("role") == "user"), "")
        reply = (
            f"收到你的需求：「{last_user[:80]}」。\n\n"
            "我先基于本站数据库做了候选筛选，并按照综合评分给你排了序。\n"
            "（提示：当前后端未配置 DASHSCOPE_API_KEY，已使用 Mock 模式。配置后即可启用真正的通义千问分析。）\n"
        )
        for ch in reply:
            yield ch
            await asyncio.sleep(0.015)
