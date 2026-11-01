from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.green_coverage import GreenCoverage
from app.schemas.green_coverage import GreenCoverageResponse, GreenCoverageSummaryResponse
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/green-coverage", tags=["Green Coverage"])


@router.get("", response_model=PaginatedResponse[GreenCoverageResponse])
def get_green_coverage(
    state: Optional[str] = Query(None, description="State filter"),
    district: Optional[str] = Query(None, description="District filter"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated green coverage / forest cover records."""
    query = db.query(GreenCoverage)

    if state:
        query = query.filter(GreenCoverage.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(
            (GreenCoverage.district.ilike(f"%{district}%")) |
            (GreenCoverage.district_name.ilike(f"%{district}%"))
        )
    if demo is not None:
        query = query.filter(GreenCoverage.is_demo == demo)

    query = query.order_by(GreenCoverage.state, GreenCoverage.district_name)
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[GreenCoverageResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/summary", response_model=GreenCoverageSummaryResponse)
def get_green_coverage_summary(
    state: str = Query(..., description="State name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns aggregated forest coverage stats for a state."""
    query = db.query(GreenCoverage).filter(GreenCoverage.state.ilike(f"%{state}%"))
    if demo is not None:
        query = query.filter(GreenCoverage.is_demo == demo)

    total_forest = query.with_entities(func.sum(GreenCoverage.total_forest_area_sqkm)).scalar() or 0.0
    total_geo = query.with_entities(func.sum(GreenCoverage.geographic_area_sqkm)).scalar() or 0.0
    avg_pct = (total_forest / total_geo * 100) if total_geo else 0.0
    very_dense = query.with_entities(func.sum(GreenCoverage.very_dense_forest)).scalar() or 0.0
    count = query.count()

    return GreenCoverageSummaryResponse(
        state=state,
        total_forest_area_sqkm=round(total_forest, 2),
        avg_forest_cover_percent=round(avg_pct, 2),
        very_dense_forest_sqkm=round(very_dense, 2),
        total_geographic_area_sqkm=round(total_geo, 2),
        district_count=count,
    )
