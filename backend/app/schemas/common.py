from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseDimensionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    state: str
    district: Optional[str] = None
    city: str
    station_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_source: str
    observed_at: Optional[datetime] = None
    data_status: str
    is_demo: bool
    created_at: datetime
