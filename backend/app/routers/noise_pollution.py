from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.noise_pollution import NoisePollution
from app.schemas.noise_pollution import NoisePollutionResponse, NoisePollutionSummaryResponse, NoiseLocationSummary
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/noise", tags=["Noise Pollution"])

CPCB_LIMITS = {
    "residential": {"day": 55.0, "night": 45.0},
    "commercial": {"day": 65.0, "night": 55.0},
    "industrial": {"day": 75.0, "night": 70.0},
    "silence": {"day": 50.0, "night": 40.0},
}


@router.get("", response_model=PaginatedResponse[NoisePollutionResponse])
def get_noise_readings(
    state: Optional[str] = Query(None, description="State filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    location_type: Optional[str] = Query(None, description="Location type (residential, commercial, industrial, silence)"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated ambient noise level readings."""
    query = db.query(NoisePollution)

    if state:
        query = query.filter(NoisePollution.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(NoisePollution.city.ilike(f"%{city}%"))
    if district:
        query = query.filter(NoisePollution.district.ilike(f"%{district}%"))
    if location_type:
        query = query.filter(NoisePollution.location_type.ilike(f"%{location_type}%"))
    if demo is not None:
        query = query.filter(NoisePollution.is_demo == demo)

    query = query.order_by(NoisePollution.observed_at.desc().nullslast(), NoisePollution.id.desc())
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[NoisePollutionResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/summary", response_model=NoisePollutionSummaryResponse)
def get_noise_summary(
    state: str = Query(..., description="State name"),
    city: str = Query(..., description="City name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns day/night noise averages by zone compared against CPCB standards."""
    query = db.query(NoisePollution).filter(
        NoisePollution.state.ilike(f"%{state}%"),
        NoisePollution.city.ilike(f"%{city}%"),
    )
    if demo is not None:
        query = query.filter(NoisePollution.is_demo == demo)

    station_count = query.count()

    stats = (
        query.with_entities(
            NoisePollution.location_type,
            func.avg(NoisePollution.day_db).label("avg_day"),
            func.avg(NoisePollution.night_db).label("avg_night"),
            func.count(NoisePollution.id).label("reading_count"),
        )
        .group_by(NoisePollution.location_type)
        .all()
    )

    levels: List[NoiseLocationSummary] = []
    for row in stats:
        loc_type = row.location_type.lower()
        limits = CPCB_LIMITS.get(loc_type, {"day": 60.0, "night": 50.0})
        levels.append(
            NoiseLocationSummary(
                location_type=row.location_type,
                avg_day_db=round(row.avg_day, 1),
                avg_night_db=round(row.avg_night, 1),
                cpcb_day_limit=limits["day"],
                cpcb_night_limit=limits["night"],
                reading_count=row.reading_count,
            )
        )

    return NoisePollutionSummaryResponse(
        state=state,
        city=city,
        station_count=station_count,
        levels=levels,
    )
