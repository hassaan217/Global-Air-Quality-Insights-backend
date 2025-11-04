# Optional data models or ODM mappings can be defined here if needed in future
from typing import Optional
from pydantic import BaseModel


class AQISnapshot(BaseModel):
    city: str
    aqi: Optional[int]
    ts: str
