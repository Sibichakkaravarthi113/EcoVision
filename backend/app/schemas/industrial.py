from typing import Optional, Dict
from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class IndustrialResponse(BaseDimensionResponse):
    industry_type: str
    industry_name: str
    compliance_status: str
    emissions_indicator: Optional[str] = None
    consent_to_operate: Optional[bool] = None
    reporting_year: int


class IndustrialSummaryResponse(BaseModel):
    state: str
    total_industries: int
    compliant_count: int
    non_compliant_count: int
    under_observation_count: int
    compliance_percent: float
    industry_type_breakdown: Dict[str, int]
