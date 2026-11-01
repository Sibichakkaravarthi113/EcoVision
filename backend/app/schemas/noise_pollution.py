from typing import List
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class NoisePollutionResponse(BaseDimensionResponse):
    location_type: str
    day_db: float
    night_db: float
    measurement_period: str


class NoiseLocationSummary(BaseModel):
    location_type: str
    avg_day_db: float
    avg_night_db: float
    cpcb_day_limit: float
    cpcb_night_limit: float
    reading_count: int


class NoisePollutionSummaryResponse(BaseModel):
    state: str
    city: str
    station_count: int
    levels: List[NoiseLocationSummary]
