from typing import Optional, Dict
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class TrafficResponse(BaseDimensionResponse):
    road_name: str
    vehicle_count_hour: Optional[int] = None
    avg_speed_kmh: Optional[float] = None
    congestion_level: str
    peak_hour: Optional[str] = None


class TrafficSummaryResponse(BaseModel):
    state: str
    city: str
    avg_speed_kmh: float
    total_roads_monitored: int
    congestion_breakdown: Dict[str, int]
