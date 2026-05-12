from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["rankings"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
