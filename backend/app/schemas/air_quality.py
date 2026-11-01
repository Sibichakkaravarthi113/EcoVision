from typing import List
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class AirQualityResponse(BaseDimensionResponse):
    parameter: str
    value: float
    unit: str
    pollutant_category: str


class PollutantSummary(BaseModel):
    parameter: str
    unit: str
    avg_value: float
    min_value: float
    max_value: float
    reading_count: int


class AirQualitySummaryResponse(BaseModel):
    state: str
    city: str
    station_count: int
    pollutants: List[PollutantSummary]
