from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.air_quality import AirQualityReading
from app.models.water_quality import WaterQualityReading
from app.models.green_coverage import GreenCoverage
from app.models.waste_management import WasteManagement
from app.models.noise_pollution import NoisePollution
from app.models.traffic import TrafficCongestion
from app.models.industrial import IndustrialActivity
from app.models.climate import ClimateReading


def check_data_availability(
    db: Session,
    state: Optional[str] = None,
    city: Optional[str] = None,
    demo: Optional[bool] = None,
) -> Dict[str, bool]:
    """
    Checks which dimensions have records in the database for a given state/city/demo mode.
    Returns: {dimension_name: bool}
    """
    models = {
        "air_quality": AirQualityReading,
        "water_quality": WaterQualityReading,
        "green_coverage": GreenCoverage,
        "waste_management": WasteManagement,
        "noise_pollution": NoisePollution,
        "traffic": TrafficCongestion,
        "industrial": IndustrialActivity,
        "climate": ClimateReading,
    }

    availability: Dict[str, bool] = {}

    for name, model in models.items():
        query = db.query(model.id)
        if state:
            query = query.filter(model.state.ilike(f"%{state}%"))
        if city:
            query = query.filter(model.city.ilike(f"%{city}%"))
        if demo is not None:
            query = query.filter(model.is_demo == demo)

        has_data = query.first() is not None
        availability[name] = has_data

    return availability
