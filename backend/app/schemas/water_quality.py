from typing import List, Optional
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class WaterQualityResponse(BaseDimensionResponse):
    parameter: str
    value: float
    unit: str
    station_code: Optional[str] = None


class WaterParameterSummary(BaseModel):
    parameter: str
    unit: str
    avg_value: float
    min_value: float
    max_value: float
    sample_count: int


class WaterQualitySummaryResponse(BaseModel):
    state: str
    district: Optional[str] = None
    station_count: int
    parameters: List[WaterParameterSummary]
