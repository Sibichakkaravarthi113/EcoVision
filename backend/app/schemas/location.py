from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    country: str
    state: str
    district: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DistrictCitiesNode(BaseModel):
    district: str
    cities: List[str]


class StateHierarchyNode(BaseModel):
    state: str
    districts: List[DistrictCitiesNode]
