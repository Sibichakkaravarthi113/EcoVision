from typing import Optional, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.industrial import IndustrialActivity
from app.schemas.industrial import IndustrialResponse, IndustrialSummaryResponse
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/industrial", tags=["Industrial Activity"])


@router.get("", response_model=PaginatedResponse[IndustrialResponse])
def get_industrial_records(
    state: Optional[str] = Query(None, description="State filter"),
    district: Optional[str] = Query(None, description="District filter"),
    city: Optional[str] = Query(None, description="City filter"),
    industry_type: Optional[str] = Query(None, description="Industry sector filter"),
    compliance_status: Optional[str] = Query(None, description="Compliance status filter"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated industrial units and compliance records."""
    query = db.query(IndustrialActivity)

    if state:
        query = query.filter(IndustrialActivity.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(IndustrialActivity.district.ilike(f"%{district}%"))
    if city:
        query = query.filter(IndustrialActivity.city.ilike(f"%{city}%"))
    if industry_type:
        query = query.filter(IndustrialActivity.industry_type.ilike(f"%{industry_type}%"))
    if compliance_status:
        query = query.filter(IndustrialActivity.compliance_status.ilike(f"%{compliance_status}%"))
    if demo is not None:
        query = query.filter(IndustrialActivity.is_demo == demo)

    query = query.order_by(IndustrialActivity.state, IndustrialActivity.city, IndustrialActivity.industry_name)
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[IndustrialResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/summary", response_model=IndustrialSummaryResponse)
def get_industrial_summary(
    state: str = Query(..., description="State name"),
    city: Optional[str] = Query(None, description="Optional city filter"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns industrial compliance rates and industry sector distribution."""
    query = db.query(IndustrialActivity).filter(IndustrialActivity.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(IndustrialActivity.city.ilike(f"%{city}%"))
    if demo is not None:
        query = query.filter(IndustrialActivity.is_demo == demo)

    total = query.count()
    compliant = query.filter(IndustrialActivity.compliance_status == "compliant").count()
    non_compliant = query.filter(IndustrialActivity.compliance_status == "non_compliant").count()
    under_observation = query.filter(IndustrialActivity.compliance_status == "under_observation").count()
    comp_pct = round((compliant / total * 100), 1) if total > 0 else 0.0

    types_rows = (
        query.with_entities(IndustrialActivity.industry_type, func.count(IndustrialActivity.id))
        .group_by(IndustrialActivity.industry_type)
        .all()
    )
    breakdown: Dict[str, int] = {row[0]: row[1] for row in types_rows}

    return IndustrialSummaryResponse(
        state=state,
        total_industries=total,
        compliant_count=compliant,
        non_compliant_count=non_compliant,
        under_observation_count=under_observation,
        compliance_percent=comp_pct,
        industry_type_breakdown=breakdown,
    )
