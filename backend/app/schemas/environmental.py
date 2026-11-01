
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EnvironmentalReadingCreate(BaseModel):
    factor: str
    parameter: str
    value: float
    unit: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str
    data_status: str
    observed_at: Optional[datetime] = None


class EnvironmentalReadingResponse(EnvironmentalReadingCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
