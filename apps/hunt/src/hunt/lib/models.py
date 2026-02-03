from pydantic import BaseModel, Field
from typing import Optional


class GeoQuery(BaseModel):
    text_query: str = Field(..., description="User's natural language request")
    location: Optional[str] = Field(
        None,
        description="Place name only (e.g. 'Dehradun, India')"
    )
    latitude: Optional[float] = Field(None, description="Latitude (optional)")
    longitude: Optional[float] = Field(None, description="Longitude (optional)")
    radius_km: float = Field(default=5.0, description="Search radius in km")
    facility_type: str = Field(default="court", description="court | academy")
