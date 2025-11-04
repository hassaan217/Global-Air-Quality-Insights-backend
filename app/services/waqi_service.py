import os
from dotenv import load_dotenv
import httpx
from typing import List

load_dotenv()
WAQI_TOKEN = os.getenv("WAQI_API_TOKEN")
BASE_WAQI = "https://api.waqi.info"

# A small seed list for top10 (expandable)
SEED_CITIES = [
    "Delhi","Dhaka","Karachi","Lahore","Beijing","Ulaanbaatar","Kathmandu",
    "Tehran","Ahmedabad","Surat","Shijiazhuang","Cairo","Bangkok","Ho Chi Minh City"
]

async def fetch_feed_for(city: str):
    url = f"{BASE_WAQI}/feed/{city}/?token={WAQI_TOKEN}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        return r.json() if r.status_code == 200 else {"status": "error"}

async def get_top_cities(limit: int = 10):
    """
    Query a seed list and return top cities by AQI (descending).
    WAQI doesn't provide a single global top10 endpoint for free users so we
    query a curated seed set.
    """
    results = []
    async with httpx.AsyncClient(timeout=10) as client:
        for city in SEED_CITIES:
            try:
                url = f"{BASE_WAQI}/feed/{city}/?token={WAQI_TOKEN}"
                r = await client.get(url)
                j = r.json()
                if j.get("status") == "ok":
                    data = j["data"]
                    name = data.get("city", {}).get("name") or city
                    aqi = data.get("aqi") or 0
                    results.append({"city": name, "aqi": int(aqi), "iaqi": data.get("iaqi", {})})
            except Exception:
                continue

    results_sorted = sorted(results, key=lambda x: x["aqi"] if x["aqi"] is not None else 0, reverse=True)
    return results_sorted[:limit]

async def get_city_data(city: str):
    j = await fetch_feed_for(city)
    if j.get("status") != "ok":
        raise RuntimeError("WAQI returned error or city not found")
    return j["data"]

# Note: WAQI doesn't have a direct hourly history endpoint in free tier.
# We'll return None and let the router fallback to DB or mock.
async def get_city_history(city: str, hours: int):
    # Placeholder - return None to let caller use DB or mock
    return None
