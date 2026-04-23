from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterable


class Message(dict):
    """简单字典，结构 {'role': 'user'|'assistant'|'system', 'content': str}."""


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def stream_chat(self, messages: Iterable[dict]) -> AsyncIterator[str]:
        """异步流式输出文本分片。"""
        ...
