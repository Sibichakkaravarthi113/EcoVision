from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class ClimateResponse(BaseDimensionResponse):
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    rainfall_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_condition: Optional[str] = None
    is_forecast: bool = False
    forecast_hour: Optional[int] = None


class ClimateSummaryResponse(BaseModel):
    state: str
    city: str
    avg_temperature_c: float
    avg_humidity_percent: float
    total_rainfall_mm: float
    avg_wind_speed_kmh: float
    latest_condition: Optional[str] = None


class CurrentWeatherResponse(BaseModel):
    city: str
    latitude: float
    longitude: float
    source: str
    current: Dict[str, Any]
    hourly_forecast: List[Dict[str, Any]]
