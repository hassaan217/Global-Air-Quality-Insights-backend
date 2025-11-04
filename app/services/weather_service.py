import os
from dotenv import load_dotenv
import httpx

load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_WEATHER = "https://api.openweathermap.org/data/2.5"

async def get_weather_by_coords(lat: float, lon: float):
    if not OPENWEATHER_KEY:
        return {}
    url = f"{BASE_WEATHER}/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
    async with httpx.AsyncClient(timeout=8) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.json()
    return {}
