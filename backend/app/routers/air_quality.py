from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.air_quality import AirQualityReading
from app.schemas.air_quality import AirQualityResponse, AirQualitySummaryResponse, PollutantSummary
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/air-quality", tags=["Air Quality"])


@router.get("", response_model=PaginatedResponse[AirQualityResponse])
def get_air_quality_readings(
    state: Optional[str] = Query(None, description="State filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    parameter: Optional[str] = Query(None, description="Pollutant parameter (e.g. PM2.5, NO2)"),
    pollutant: Optional[str] = Query(None, description="Alias for parameter"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated air quality readings with filtering options."""
    query = db.query(AirQualityReading)

    if state:
        query = query.filter(AirQualityReading.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(AirQualityReading.city.ilike(f"%{city}%"))
    if district:
        query = query.filter(AirQualityReading.district.ilike(f"%{district}%"))
    target_pollutant = pollutant or parameter
    if target_pollutant:
        query = query.filter(AirQualityReading.parameter.ilike(f"%{target_pollutant}%"))
    if demo is not None:
        query = query.filter(AirQualityReading.is_demo == demo)

    query = query.order_by(AirQualityReading.observed_at.desc().nullslast(), AirQualityReading.id.desc())
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[AirQualityResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/pollutants", response_model=List[str])
def get_pollutants(db: Session = Depends(get_db)):
    """Returns list of unique monitored pollutants."""
    results = (
        db.query(AirQualityReading.parameter)
        .distinct()
        .order_by(AirQualityReading.parameter)
        .all()
    )
    return [r[0] for r in results]


@router.get("/states", response_model=List[str])
def get_states(db: Session = Depends(get_db)):
    """Returns list of states with air quality readings."""
    results = (
        db.query(AirQualityReading.state)
        .distinct()
        .order_by(AirQualityReading.state)
        .all()
    )
    return [r[0] for r in results]


@router.get("/summary", response_model=AirQualitySummaryResponse)
def get_air_quality_summary(
    state: str = Query(..., description="State name"),
    city: str = Query(..., description="City name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns pollutant averages, min, max and station count for a city."""
    base_q = db.query(AirQualityReading).filter(
        AirQualityReading.state.ilike(f"%{state}%"),
        AirQualityReading.city.ilike(f"%{city}%"),
    )
    if demo is not None:
        base_q = base_q.filter(AirQualityReading.is_demo == demo)

    station_count = base_q.distinct(AirQualityReading.station_name).count()

    pollutant_stats = (
        base_q.with_entities(
            AirQualityReading.parameter,
            AirQualityReading.unit,
            func.avg(AirQualityReading.value).label("avg_val"),
            func.min(AirQualityReading.value).label("min_val"),
            func.max(AirQualityReading.value).label("max_val"),
            func.count(AirQualityReading.id).label("count_val"),
        )
        .group_by(AirQualityReading.parameter, AirQualityReading.unit)
        .all()
    )

    pollutant_summaries = [
        PollutantSummary(
            parameter=row.parameter,
            unit=row.unit,
            avg_value=round(row.avg_val, 2),
            min_value=round(row.min_val, 2),
            max_value=round(row.max_val, 2),
            reading_count=row.count_val,
        )
        for row in pollutant_stats
    ]

    return AirQualitySummaryResponse(
        state=state,
        city=city,
        station_count=station_count,
        pollutants=pollutant_summaries,
    )
