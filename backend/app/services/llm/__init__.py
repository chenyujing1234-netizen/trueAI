from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.mock import MockLLM
from app.services.llm.qwen import QwenLLM


def get_llm() -> LLMProvider:
    provider = (settings.LLM_PROVIDER or "qwen").lower()
    if provider == "qwen" and settings.DASHSCOPE_API_KEY:
        return QwenLLM()
    return MockLLM()


__all__ = ["LLMProvider", "QwenLLM", "MockLLM", "get_llm"]
