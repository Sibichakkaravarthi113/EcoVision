from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.water_quality import WaterQualityReading
from app.schemas.water_quality import WaterQualityResponse, WaterQualitySummaryResponse, WaterParameterSummary
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/water-quality", tags=["Water Quality"])


@router.get("", response_model=PaginatedResponse[WaterQualityResponse])
def get_water_quality_readings(
    state: Optional[str] = Query(None, description="State filter"),
    district: Optional[str] = Query(None, description="District filter"),
    city: Optional[str] = Query(None, description="City filter"),
    station: Optional[str] = Query(None, description="Station name filter"),
    parameter: Optional[str] = Query(None, description="Water parameter filter"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated water quality readings with filtering options."""
    query = db.query(WaterQualityReading)

    if state:
        query = query.filter(WaterQualityReading.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(WaterQualityReading.district.ilike(f"%{district}%"))
    if city:
        query = query.filter(WaterQualityReading.city.ilike(f"%{city}%"))
    if station:
        query = query.filter(WaterQualityReading.station_name.ilike(f"%{station}%"))
    if parameter:
        query = query.filter(WaterQualityReading.parameter.ilike(f"%{parameter}%"))
    if demo is not None:
        query = query.filter(WaterQualityReading.is_demo == demo)

    query = query.order_by(WaterQualityReading.observed_at.desc().nullslast(), WaterQualityReading.id.desc())
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[WaterQualityResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/parameters", response_model=List[str])
def get_water_parameters(db: Session = Depends(get_db)):
    """Returns list of unique monitored water parameters."""
    results = (
        db.query(WaterQualityReading.parameter)
        .distinct()
        .order_by(WaterQualityReading.parameter)
        .all()
    )
    return [r[0] for r in results]


@router.get("/summary", response_model=WaterQualitySummaryResponse)
def get_water_quality_summary(
    state: str = Query(..., description="State name"),
    district: Optional[str] = Query(None, description="District name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns parameter averages and sample counts for a state/district."""
    base_q = db.query(WaterQualityReading).filter(WaterQualityReading.state.ilike(f"%{state}%"))
    if district:
        base_q = base_q.filter(WaterQualityReading.district.ilike(f"%{district}%"))
    if demo is not None:
        base_q = base_q.filter(WaterQualityReading.is_demo == demo)

    station_count = base_q.distinct(WaterQualityReading.station_name).count()

    stats = (
        base_q.with_entities(
            WaterQualityReading.parameter,
            WaterQualityReading.unit,
            func.avg(WaterQualityReading.value).label("avg_val"),
            func.min(WaterQualityReading.value).label("min_val"),
            func.max(WaterQualityReading.value).label("max_val"),
            func.count(WaterQualityReading.id).label("count_val"),
        )
        .group_by(WaterQualityReading.parameter, WaterQualityReading.unit)
        .all()
    )

    summaries = [
        WaterParameterSummary(
            parameter=row.parameter,
            unit=row.unit,
            avg_value=round(row.avg_val, 2),
            min_value=round(row.min_val, 2),
            max_value=round(row.max_val, 2),
            sample_count=row.count_val,
        )
        for row in stats
    ]

    return WaterQualitySummaryResponse(
        state=state,
        district=district,
        station_count=station_count,
        parameters=summaries,
    )
