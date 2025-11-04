from typing import List
from datetime import datetime, timedelta
from app.database.mongo import get_db

async def save_city_snapshot(city_name: str, snapshot: dict):
    db = get_db()
    # normalized doc
    doc = {
        "name": city_name,
        "aqi": snapshot.get("aqi"),
        "pollutants": snapshot.get("pollutants", {}),
        "weather": snapshot.get("weather", {}),
        "timestamp": snapshot.get("timestamp", datetime.utcnow())
    }
    await db.city_history.insert_one(doc)

async def get_city_history_from_db(city_name: str, hours: int = 48) -> List[dict]:
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cursor = db.city_history.find({"name": city_name, "timestamp": {"$gte": cutoff}}).sort("timestamp", 1)
    results = []
    async for doc in cursor:
        results.append({
            "time": doc["timestamp"].isoformat(),
            "aqi": doc.get("aqi", 0)
        })
    return results
