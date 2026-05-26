import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.routers import (
    auth,
    categories,
    tools,
    reviews,
    rankings,
    stats,
    search,
    analytics,
)
from app.api.mcp_server import SERVER_CARD, mcp_sse_app, mcp_streamable_app
from app.middleware.tracking import TrackingMiddleware

app = FastAPI(
    title="TrueAI API",
    description="真选AI (TrueAI) — 让你不再纠结选哪个 AI 工具",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrackingMiddleware)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "trueai-api"}


# Smithery / 通用 MCP 注册中心通过这个 well-known 文件描述协议、工具与配置 schema。
# 见 https://smithery.ai/docs/build/publish#troubleshooting
_SERVER_CARD = os.path.join(
    os.path.dirname(__file__), "static", "well-known", "mcp", "server-card.json"
)


@app.get("/.well-known/mcp/server-card.json", include_in_schema=False)
def mcp_server_card():
    return FileResponse(_SERVER_CARD, media_type="application/json")


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["rankings"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# MCP server, two transports mounted on the same uvicorn process.
#
# Streamable HTTP (preferred, single URL, default for Smithery / modern hosts):
#   { "mcpServers": { "trueai": { "url": "https://www.shiflowai.cloud/mcp" } } }
#
# Legacy SSE (kept for older clients):
#   GET  /mcp-sse/sse        — event stream
#   POST /mcp-sse/messages/  — client → server messages
#   { "mcpServers": { "trueai": { "url": "https://www.shiflowai.cloud/mcp-sse/sse" } } }
app.mount("/mcp", mcp_streamable_app)
app.mount("/mcp-sse", mcp_sse_app)


# Static "server card" so directories (Smithery etc.) can skip auto-scan.
@app.get("/.well-known/mcp/server-card.json")
def mcp_server_card():
    return SERVER_CARD
