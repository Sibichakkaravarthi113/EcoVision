from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.waste_management import WasteManagement
from app.schemas.waste_management import WasteManagementResponse, WasteManagementSummaryResponse
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/waste-management", tags=["Waste Management"])


@router.get("", response_model=PaginatedResponse[WasteManagementResponse])
def get_waste_management_records(
    state: Optional[str] = Query(None, description="State filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated municipal waste management records."""
    query = db.query(WasteManagement)

    if state:
        query = query.filter(WasteManagement.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(WasteManagement.city.ilike(f"%{city}%"))
    if district:
        query = query.filter(WasteManagement.district.ilike(f"%{district}%"))
    if demo is not None:
        query = query.filter(WasteManagement.is_demo == demo)

    query = query.order_by(WasteManagement.state, WasteManagement.city)
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[WasteManagementResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/summary", response_model=WasteManagementSummaryResponse)
def get_waste_management_summary(
    state: str = Query(..., description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns waste generation, collection, and recycling summary."""
    query = db.query(WasteManagement).filter(WasteManagement.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(WasteManagement.city.ilike(f"%{city}%"))
    if demo is not None:
        query = query.filter(WasteManagement.is_demo == demo)

    gen = query.with_entities(func.sum(WasteManagement.generated_tonnes_day)).scalar() or 0.0
    col = query.with_entities(func.sum(WasteManagement.collected_tonnes_day)).scalar() or 0.0
    proc = query.with_entities(func.sum(WasteManagement.processed_tonnes_day)).scalar() or 0.0
    rec_pct = query.with_entities(func.avg(WasteManagement.recycling_percent)).scalar() or 0.0
    eff = round((col / gen * 100), 2) if gen > 0 else 0.0

    return WasteManagementSummaryResponse(
        state=state,
        city=city,
        total_generated_tonnes_day=round(gen, 2),
        total_collected_tonnes_day=round(col, 2),
        total_processed_tonnes_day=round(proc, 2),
        avg_recycling_percent=round(rec_pct, 2),
        collection_efficiency_percent=eff,
    )
