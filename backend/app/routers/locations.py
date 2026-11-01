from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.location import Location
from app.schemas.location import StateHierarchyNode, DistrictCitiesNode

router = APIRouter(prefix="/api/locations", tags=["Locations"])


@router.get("/states", response_model=List[str])
def get_states(db: Session = Depends(get_db)):
    """Returns a sorted list of unique states."""
    results = (
        db.query(Location.state)
        .distinct()
        .filter(Location.state.isnot(None), Location.state != "")
        .order_by(Location.state)
        .all()
    )
    return [r[0] for r in results]


@router.get("/districts", response_model=List[str])
def get_districts(
    state: Optional[str] = Query(None, description="Filter by state name"),
    db: Session = Depends(get_db),
):
    """Returns a sorted list of unique districts for a given state."""
    query = (
        db.query(Location.district)
        .distinct()
        .filter(Location.district.isnot(None), Location.district != "")
    )
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    results = query.order_by(Location.district).all()
    return [r[0] for r in results]


@router.get("/cities", response_model=List[str])
def get_cities(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    db: Session = Depends(get_db),
):
    """Returns a sorted list of unique cities for a given state and district."""
    query = (
        db.query(Location.city)
        .distinct()
        .filter(Location.city.isnot(None), Location.city != "")
    )
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(Location.district.ilike(f"%{district}%"))
    results = query.order_by(Location.city).all()
    return [r[0] for r in results]


@router.get("/all", response_model=List[StateHierarchyNode])
def get_all_locations(db: Session = Depends(get_db)):
    """Returns the full geographic hierarchy: State -> Districts -> Cities."""
    locations = (
        db.query(Location)
        .order_by(Location.state, Location.district, Location.city)
        .all()
    )

    hierarchy: dict[str, dict[str, set[str]]] = {}

    for loc in locations:
        st = loc.state or "Unknown"
        dist = loc.district or loc.city or "General"
        city = loc.city

        if st not in hierarchy:
            hierarchy[st] = {}
        if dist not in hierarchy[st]:
            hierarchy[st][dist] = set()
        if city:
            hierarchy[st][dist].add(city)

    result = []
    for st, dists in sorted(hierarchy.items()):
        district_nodes = []
        for dist, cities in sorted(dists.items()):
            district_nodes.append(
                DistrictCitiesNode(district=dist, cities=sorted(list(cities)))
            )
        result.append(StateHierarchyNode(state=st, districts=district_nodes))

    return result
