from typing import Optional, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.traffic import TrafficCongestion
from app.schemas.traffic import TrafficResponse, TrafficSummaryResponse
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/traffic", tags=["Traffic Congestion"])


@router.get("", response_model=PaginatedResponse[TrafficResponse])
def get_traffic_readings(
    state: Optional[str] = Query(None, description="State filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    congestion_level: Optional[str] = Query(None, description="Congestion level (low, moderate, high, severe)"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated traffic monitoring readings."""
    query = db.query(TrafficCongestion)

    if state:
        query = query.filter(TrafficCongestion.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(TrafficCongestion.city.ilike(f"%{city}%"))
    if district:
        query = query.filter(TrafficCongestion.district.ilike(f"%{district}%"))
    if congestion_level:
        query = query.filter(TrafficCongestion.congestion_level.ilike(f"%{congestion_level}%"))
    if demo is not None:
        query = query.filter(TrafficCongestion.is_demo == demo)

    query = query.order_by(TrafficCongestion.observed_at.desc().nullslast(), TrafficCongestion.id.desc())
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[TrafficResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/summary", response_model=TrafficSummaryResponse)
def get_traffic_summary(
    state: str = Query(..., description="State name"),
    city: str = Query(..., description="City name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns average speed and congestion distribution for a city."""
    query = db.query(TrafficCongestion).filter(
        TrafficCongestion.state.ilike(f"%{state}%"),
        TrafficCongestion.city.ilike(f"%{city}%"),
    )
    if demo is not None:
        query = query.filter(TrafficCongestion.is_demo == demo)

    total_roads = query.count()
    avg_speed = query.with_entities(func.avg(TrafficCongestion.avg_speed_kmh)).scalar() or 0.0

    breakdown_rows = (
        query.with_entities(TrafficCongestion.congestion_level, func.count(TrafficCongestion.id))
        .group_by(TrafficCongestion.congestion_level)
        .all()
    )
    breakdown: Dict[str, int] = {row[0]: row[1] for row in breakdown_rows}

    return TrafficSummaryResponse(
        state=state,
        city=city,
        avg_speed_kmh=round(avg_speed, 1),
        total_roads_monitored=total_roads,
        congestion_breakdown=breakdown,
    )
