from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.air_quality import AirQualityReading
from app.models.water_quality import WaterQualityReading
from app.models.green_coverage import GreenCoverage
from app.models.waste_management import WasteManagement
from app.models.noise_pollution import NoisePollution
from app.models.traffic import TrafficCongestion
from app.models.industrial import IndustrialActivity
from app.models.climate import ClimateReading
from app.models.location import Location

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
def get_health(db: Session = Depends(get_db)):
    """Health check endpoint reporting system status and record counts across all tables."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    counts = {
        "air_quality": db.query(AirQualityReading).count() if db_status == "connected" else 0,
        "water_quality": db.query(WaterQualityReading).count() if db_status == "connected" else 0,
        "green_coverage": db.query(GreenCoverage).count() if db_status == "connected" else 0,
        "waste_management": db.query(WasteManagement).count() if db_status == "connected" else 0,
        "noise_pollution": db.query(NoisePollution).count() if db_status == "connected" else 0,
        "traffic": db.query(TrafficCongestion).count() if db_status == "connected" else 0,
        "industrial": db.query(IndustrialActivity).count() if db_status == "connected" else 0,
        "climate": db.query(ClimateReading).count() if db_status == "connected" else 0,
        "locations": db.query(Location).count() if db_status == "connected" else 0,
    }

    return {
        "status": "ok",
        "version": "1.0.0",
        "db_status": db_status,
        "record_counts": counts,
    }
