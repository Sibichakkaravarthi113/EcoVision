from app.database import Base
from app.models.air_quality import AirQualityReading
from app.models.water_quality import WaterQualityReading
from app.models.green_coverage import GreenCoverage
from app.models.waste_management import WasteManagement
from app.models.noise_pollution import NoisePollution
from app.models.traffic import TrafficCongestion
from app.models.industrial import IndustrialActivity
from app.models.climate import ClimateReading
from app.models.location import Location

__all__ = [
    "Base",
    "AirQualityReading",
    "WaterQualityReading",
    "GreenCoverage",
    "WasteManagement",
    "NoisePollution",
    "TrafficCongestion",
    "IndustrialActivity",
    "ClimateReading",
    "Location",
]