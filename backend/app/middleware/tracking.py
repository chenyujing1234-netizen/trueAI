"""
访问记录中间件：每次 API 请求完成后，异步写入 page_views 表。
- 忽略健康检查、静态资源等无意义路径
- 异步写入，不阻塞请求响应
- 从 X-Forwarded-For 等代理头中正确提取真实 IP
"""

import asyncio
import time
from typing import Callable

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.db import SessionLocal
from app.models.page_view import PageView

# 不记录的路径前缀（健康检查、文档等）
_SKIP_PATHS = {
    "/api/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}

# 不记录的路径前缀（analytics 自身的查询，防止刷量）
_SKIP_PREFIXES = ("/api/analytics",)


def _get_real_ip(request: Request) -> str:
    """优先从代理头获取真实客户端 IP。"""
    for header in ("x-forwarded-for", "x-real-ip", "cf-connecting-ip"):
        val = request.headers.get(header)
        if val:
            return val.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _should_skip(path: str) -> bool:
    if path in _SKIP_PATHS:
        return True
    return any(path.startswith(p) for p in _SKIP_PREFIXES)


def _write_page_view(
    ip: str,
    path: str,
    method: str,
    status_code: int,
    response_time_ms: int,
    user_agent: str | None,
    referer: str | None,
) -> None:
    """在独立的数据库 Session 中写入一条访问记录（在线程池执行）。"""
    db: Session = SessionLocal()
    try:
        pv = PageView(
            ip=ip[:64],
            path=path[:512],
            method=method[:8],
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_agent=(user_agent or "")[:512] or None,
            referer=(referer or "")[:512] or None,
        )
        db.add(pv)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


class TrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        if _should_skip(path):
            return await call_next(request)

        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        ip         = _get_real_ip(request)
        method     = request.method
        status     = response.status_code
        user_agent = request.headers.get("user-agent")
        referer    = request.headers.get("referer")

        # 异步写入，不等待结果，不影响响应速度
        asyncio.get_event_loop().run_in_executor(
            None,
            _write_page_view,
            ip, path, method, status, elapsed_ms, user_agent, referer,
        )

        return response
