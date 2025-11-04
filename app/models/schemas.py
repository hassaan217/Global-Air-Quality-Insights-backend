from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class PollutantData(BaseModel):
    pm25: Optional[float] = 0
    pm10: Optional[float] = 0
    o3: Optional[float] = 0
    no2: Optional[float] = 0
    so2: Optional[float] = 0
    co: Optional[float] = 0

class WeatherData(BaseModel):
    temp: Optional[float] = None
    humidity: Optional[int] = None
    wind: Optional[float] = None

class CityResponse(BaseModel):
    name: str
    aqi: int
    pollutants: PollutantData
    weather: WeatherData
    timestamp: datetime

class CityHistoryItem(BaseModel):
    time: str
    aqi: int

class TopCity(BaseModel):
    city: str
    aqi: int
