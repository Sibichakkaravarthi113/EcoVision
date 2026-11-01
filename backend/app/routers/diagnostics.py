from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    AirQualityReading,
    GreenCoverage,
    IndustrialActivity,
    NoisePollution,
    TrafficCongestion,
    WasteManagement,
    WaterQualityReading,
)

router = APIRouter(prefix="/api/diagnostics", tags=["Diagnostics"])


@router.get("/database")
def get_database_diagnostics(db: Session = Depends(get_db)):
    """Return safe, read-only record counts for the environmental tables."""
    return {
        "database_dialect": db.get_bind().dialect.name,
        "record_counts": {
            "air_quality": db.query(AirQualityReading).count(),
            "water_quality": db.query(WaterQualityReading).count(),
            "green_coverage": db.query(GreenCoverage).count(),
            "waste_management": db.query(WasteManagement).count(),
            "noise_pollution": db.query(NoisePollution).count(),
            "traffic": db.query(TrafficCongestion).count(),
            "industrial_activity": db.query(IndustrialActivity).count(),
        },
    }
