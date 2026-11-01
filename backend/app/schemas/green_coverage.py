from pydantic import BaseModel
from app.schemas.common import BaseDimensionResponse


class GreenCoverageResponse(BaseDimensionResponse):
    district_name: str
    total_forest_area_sqkm: float
    very_dense_forest: float
    moderate_dense_forest: float
    open_forest: float
    forest_cover_percent: float
    geographic_area_sqkm: float
    data_year: int


class GreenCoverageSummaryResponse(BaseModel):
    state: str
    total_forest_area_sqkm: float
    avg_forest_cover_percent: float
    total_geographic_area_sqkm: float
    district_count: int
