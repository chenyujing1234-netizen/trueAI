from __future__ import annotations

import asyncio
from typing import AsyncIterator, Iterable

from app.core.config import settings
from app.services.llm.base import LLMProvider


class QwenLLM(LLMProvider):
    """阿里云 DashScope 通义千问流式封装。"""

    name = "qwen"

    def __init__(self, model: str | None = None) -> None:
        import dashscope  # noqa: WPS433

        dashscope.api_key = settings.DASHSCOPE_API_KEY
        self._dashscope = dashscope
        self._model = model or settings.QWEN_MODEL

    async def stream_chat(self, messages: Iterable[dict]) -> AsyncIterator[str]:
        loop = asyncio.get_running_loop()
        q: asyncio.Queue[str | None] = asyncio.Queue()

        messages_list = list(messages)
        model = self._model

        def _producer() -> None:
            try:
                resp = self._dashscope.Generation.call(
                    model=model,
                    messages=messages_list,
                    result_format="message",
                    stream=True,
                    incremental_output=True,
                )
                for item in resp:
                    try:
                        status = getattr(item, "status_code", 200)
                        if status != 200:
                            err = f"[Qwen Error {status}] {getattr(item, 'message', '')}"
                            loop.call_soon_threadsafe(q.put_nowait, err)
                            break
                        out = item.output
                        choices = out.get("choices") if isinstance(out, dict) else None
                        if choices:
                            delta = choices[0].get("message", {}).get("content", "")
                            if delta:
                                loop.call_soon_threadsafe(q.put_nowait, delta)
                    except Exception as e:  # noqa: BLE001
                        loop.call_soon_threadsafe(q.put_nowait, f"[stream parse err] {e}")
                        break
            except Exception as e:  # noqa: BLE001
                loop.call_soon_threadsafe(q.put_nowait, f"[qwen call err] {e}")
            finally:
                loop.call_soon_threadsafe(q.put_nowait, None)

        loop.run_in_executor(None, _producer)

        while True:
            item = await q.get()
            if item is None:
                break
            yield item
