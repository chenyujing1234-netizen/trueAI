"""
访问统计接口。
所有接口均不需要认证（内部使用），可按需在 main.py 加 IP 白名单保护。
"""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.page_view import PageView

router = APIRouter()


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────

def _date_range(days: int):
    """返回最近 N 天的起止 datetime。"""
    end   = datetime.utcnow()
    start = end - timedelta(days=days - 1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, end


# ─────────────────────────────────────────────
# 接口
# ─────────────────────────────────────────────

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """今日 PV / UV、昨日、累计、平均响应时间。"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yest_start  = today_start - timedelta(days=1)

    def _pv_uv(since: datetime, until: datetime):
        pv = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= since, PageView.created_at < until
        ).scalar() or 0
        uv = db.query(func.count(func.distinct(PageView.ip))).filter(
            PageView.created_at >= since, PageView.created_at < until
        ).scalar() or 0
        return pv, uv

    today_pv,  today_uv  = _pv_uv(today_start, datetime.utcnow())
    yest_pv,   yest_uv   = _pv_uv(yest_start,  today_start)
    total_pv = db.query(func.count(PageView.id)).scalar() or 0
    total_uv = db.query(func.count(func.distinct(PageView.ip))).scalar() or 0
    avg_rt   = db.query(func.avg(PageView.response_time_ms)).filter(
        PageView.response_time_ms.isnot(None)
    ).scalar()

    return {
        "today":     {"pv": today_pv, "uv": today_uv},
        "yesterday": {"pv": yest_pv,  "uv": yest_uv},
        "total":     {"pv": total_pv, "uv": total_uv},
        "avg_response_ms": round(avg_rt or 0, 1),
    }


@router.get("/daily")
def get_daily(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """最近 N 天每日 PV / UV 趋势。"""
    start, _ = _date_range(days)

    rows = (
        db.query(
            func.date(PageView.created_at).label("day"),
            func.count(PageView.id).label("pv"),
            func.count(func.distinct(PageView.ip)).label("uv"),
        )
        .filter(PageView.created_at >= start)
        .group_by(func.date(PageView.created_at))
        .order_by(func.date(PageView.created_at))
        .all()
    )

    # 补齐没有数据的日期为 0
    result_map = {str(r.day): {"pv": r.pv, "uv": r.uv} for r in rows}
    output = []
    for i in range(days):
        d = (start + timedelta(days=i)).date()
        key = str(d)
        output.append({
            "date": key,
            **result_map.get(key, {"pv": 0, "uv": 0}),
        })
    return output


@router.get("/top-pages")
def get_top_pages(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """最近 N 天访问量最多的页面。"""
    start, _ = _date_range(days)
    rows = (
        db.query(
            PageView.path,
            func.count(PageView.id).label("pv"),
            func.count(func.distinct(PageView.ip)).label("uv"),
        )
        .filter(PageView.created_at >= start)
        .group_by(PageView.path)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
        .all()
    )
    return [{"path": r.path, "pv": r.pv, "uv": r.uv} for r in rows]


@router.get("/top-ips")
def get_top_ips(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """最近 N 天访问量最多的 IP（用于发现爬虫/异常流量）。"""
    start, _ = _date_range(days)
    rows = (
        db.query(
            PageView.ip,
            func.count(PageView.id).label("pv"),
            func.count(func.distinct(PageView.path)).label("pages"),
        )
        .filter(PageView.created_at >= start)
        .group_by(PageView.ip)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
        .all()
    )
    return [{"ip": r.ip, "pv": r.pv, "pages": r.pages} for r in rows]


@router.get("/recent")
def get_recent(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """最近的访问记录（实时日志）。"""
    rows = (
        db.query(PageView)
        .order_by(PageView.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id":              r.id,
            "ip":              r.ip,
            "path":            r.path,
            "method":          r.method,
            "status_code":     r.status_code,
            "response_time_ms": r.response_time_ms,
            "user_agent":      r.user_agent,
            "referer":         r.referer,
            "created_at":      r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/hourly")
def get_hourly(
    days: int = Query(1, ge=1, le=7),
    db: Session = Depends(get_db),
):
    """最近 N 天按小时分布（用于分析高峰时段）。"""
    start, _ = _date_range(days)
    rows = (
        db.query(
            func.hour(PageView.created_at).label("hour"),
            func.count(PageView.id).label("pv"),
        )
        .filter(PageView.created_at >= start)
        .group_by(func.hour(PageView.created_at))
        .order_by(func.hour(PageView.created_at))
        .all()
    )
    hour_map = {r.hour: r.pv for r in rows}
    return [{"hour": h, "pv": hour_map.get(h, 0)} for h in range(24)]
