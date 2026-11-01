from typing import Optional
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class WasteManagementResponse(BaseDimensionResponse):
    waste_category: str
    generated_tonnes_day: float
    collected_tonnes_day: float
    processed_tonnes_day: float
    recycling_percent: float
    landfill_sites: Optional[int] = None
    reporting_year: int


class WasteManagementSummaryResponse(BaseModel):
    state: str
    city: Optional[str] = None
    total_generated_tonnes_day: float
    total_collected_tonnes_day: float
    total_processed_tonnes_day: float
    avg_recycling_percent: float
    collection_efficiency_percent: float
