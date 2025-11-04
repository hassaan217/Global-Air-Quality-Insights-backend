from fastapi import APIRouter, HTTPException, Query
from app.services.waqi_service import get_city_data, get_city_history
from app.services.weather_service import get_weather_by_coords
from app.database.history import save_city_snapshot, get_city_history_from_db
from app.models.schemas import CityResponse, CityHistoryItem
from datetime import datetime
from typing import List

router = APIRouter()

# Mock fallback if no DB/history
def generate_mock_history(hours=48):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    return [
        {"time": (now - timedelta(hours=i)).isoformat(), "aqi": 150 + (i % 10)}
        for i in reversed(range(hours))
    ]







@router.get("/details", response_model=CityResponse)
async def city_details(name: str = Query(..., description="City name (e.g., Karachi)")):
    """
    Returns current AQI + pollutants + weather for a city.
    Tries live WAQI -> save snapshot to DB -> return.
    """
    try:
        data = await get_city_data(name)
    except Exception as e:
        # If WAQI failed, attempt to read latest from DB
        db_history = await get_city_history_from_db(name, 1)
        if db_history:
            latest = db_history[-1]
            return {
                "name": name,
                "aqi": latest["aqi"],
                "pollutants": {},
                "weather": {},
                "timestamp": datetime.utcnow()
            }
        raise HTTPException(status_code=500, detail=f"Failed to fetch WAQI data: {str(e)}")

    # extract pollutants
    iaqi = data.get("iaqi", {})
    pollutants = {
        "pm25": iaqi.get("pm25", {}).get("v", 0),
        "pm10": iaqi.get("pm10", {}).get("v", 0),
        "o3": iaqi.get("o3", {}).get("v", 0),
        "no2": iaqi.get("no2", {}).get("v", 0),
        "so2": iaqi.get("so2", {}).get("v", 0),
        "co": iaqi.get("co", {}).get("v", 0)
    }

    # coords -> weather
    coords = data.get("city", {}).get("geo", [None, None])
    weather = {}
    if coords and coords[0] is not None:
        w = await get_weather_by_coords(coords[0], coords[1])
        if w:
            weather = {
                "temp": w.get("main", {}).get("temp"),
                "humidity": w.get("main", {}).get("humidity"),
                "wind": w.get("wind", {}).get("speed")
            }

    resp = {
        "name": data.get("city", {}).get("name") or name,
        "aqi": int(data.get("aqi") or 0),
        "pollutants": pollutants,
        "weather": weather,
        "timestamp": datetime.utcnow()
    }

    # save snapshot to DB (fire and forget)
    try:
        await save_city_snapshot(resp["name"], resp)
    except Exception as e:
        print("Warning: failed to save snapshot:", e)

    return resp

@router.get("/history", response_model=List[CityHistoryItem])
async def city_history(name: str = Query(...), period: str = Query("48h")):
    # parse period
    if period.endswith("h"):
        hours = int(period[:-1])
    elif period.endswith("d"):
        hours = int(period[:-1]) * 24
    else:
        hours = 48

    # try DB
    try:
        db_hist = await get_city_history_from_db(name, hours)
        if db_hist and len(db_hist) > 0:
            return db_hist
    except Exception as e:
        print("DB history read error:", e)

    # fallback to WAQI API history (not available) or mock
    mock = generate_mock_history(hours)
    return mock
