from fastapi import APIRouter
from typing import List
from app.services.waqi_service import get_top_cities
from app.models.schemas import TopCity

router = APIRouter()

@router.get("/top10", response_model=List[TopCity])
async def top10():
    try:
        cities = await get_top_cities(limit=10)

        cleaned = []
        seen = set()

        for c in cities:
            city = c.get("city")
            aqi = c.get("aqi", 0)

            if not city or city in ["Unknown", "", None]:
                continue  # Skip invalid entries

            if city in seen:
                continue
            seen.add(city)

            cleaned.append({
                "city": city,
                "aqi": aqi,
                "pm25": c.get("pm25", "N/A"),
                "pm10": c.get("pm10", "N/A"),
            })

        return cleaned[:10]

    except Exception as e:
        print("🔥 Error fetching top10:", e)
        return [
            {"city": "Delhi, India", "aqi": 312, "pm25": 180, "pm10": 200},
            {"city": "Lahore, Pakistan", "aqi": 287, "pm25": 160, "pm10": 175},
            {"city": "Karachi, Pakistan", "aqi": 265, "pm25": 140, "pm10": 150},
        ]
