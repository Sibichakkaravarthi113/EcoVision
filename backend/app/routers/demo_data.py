import json
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.demo_environmental_record import DemoEnvironmentalRecord, DemoLocation

router = APIRouter(prefix="/api/demo", tags=["Synthetic Demo Data"])


def _record_to_dict(record: DemoEnvironmentalRecord) -> dict[str, Any]:
    data = json.loads(record.payload)
    data.update(
        {
            "id": record.id,
            "module": record.module,
            "state": record.state,
            "district": record.district,
            "city": record.city,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "observed_at": record.observed_at.isoformat() if record.observed_at else None,
            "source": record.source,
            "data_status": record.data_status,
            "is_real_measurement": record.is_real_measurement,
        }
    )
    return data


@router.get("/locations")
def get_demo_locations(
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(DemoLocation)
    if state:
        query = query.filter(DemoLocation.state == state)
    return [
        {
            "state": item.state,
            "district": item.district,
            "city": item.city,
            "latitude": item.latitude,
            "longitude": item.longitude,
        }
        for item in query.order_by(DemoLocation.state, DemoLocation.city).all()
    ]


@router.get("/{module}")
def get_demo_records(
    module: str,
    state: str | None = Query(default=None),
    district: str | None = Query(default=None),
    city: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(DemoEnvironmentalRecord).filter(
        DemoEnvironmentalRecord.module == module,
        DemoEnvironmentalRecord.data_status == "synthetic_demo",
    )
    if state:
        query = query.filter(DemoEnvironmentalRecord.state == state)
    if district:
        query = query.filter(DemoEnvironmentalRecord.district == district)
    if city:
        query = query.filter(DemoEnvironmentalRecord.city == city)
    return {
        "module": module,
        "data_status": "synthetic_demo",
        "records": [_record_to_dict(item) for item in query.order_by(DemoEnvironmentalRecord.observed_at.desc()).all()],
    }
