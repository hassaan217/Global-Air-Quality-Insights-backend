from celery import Celery
from app.services.waqi_service import get_top_cities
from app.database.history import save_city_data
from app.services.weather_service import get_weather_data
from app.database.mongo import get_db
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Celery
REDIS_URL = os.getenv("REDIS_URL")
celery_app = Celery(
    "air_quality_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-top-cities": {
            "task": "app.tasks.scheduler.fetch_and_store_top_cities",
            "schedule": 600.0,  # Run every 10 minutes
        },
    },
)

@celery_app.task
async def fetch_and_store_top_cities():
    """
    Periodic task to fetch and store data for top polluted cities
    """
    try:
        # Get top 10 cities
        top_cities = await get_top_cities()
        
        # Fetch and store data for each city
        for city in top_cities:
            city_name = city.get("city", {}).get("name", "")
            if city_name:
                # Get detailed city data
                city_data = await get_city_data(city_name)
                
                # Get weather data
                weather_data = await get_weather_data(city_name)
                
                # Combine data
                combined_data = {
                    "name": city_data.get("city", {}).get("name", city_name),
                    "aqi": city_data.get("aqi", 0),
                    "pollutants": {
                        "pm25": city_data.get("iaqi", {}).get("pm25", {}).get("v", 0),
                        "pm10": city_data.get("iaqi", {}).get("pm10", {}).get("v", 0),
                        "o3": city_data.get("iaqi", {}).get("o3", {}).get("v", 0),
                        "no2": city_data.get("iaqi", {}).get("no2", {}).get("v", 0),
                        "so2": city_data.get("iaqi", {}).get("so2", {}).get("v", 0),
                        "co": city_data.get("iaqi", {}).get("co", {}).get("v", 0),
                    },
                    "weather": {
                        "temp": weather_data.get("main", {}).get("temp", 0),
                        "humidity": weather_data.get("main", {}).get("humidity", 0),
                        "wind": weather_data.get("wind", {}).get("speed", 0),
                    },
                    "timestamp": datetime.now()
                }
                
                # Save to database
                await save_city_data(combined_data)
        
        return {"status": "success", "message": "Top cities data updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_scheduler():
    """
    Start the Celery scheduler
    """
    # In a production environment, you would run Celery as a separate service
    # For development, we'll just log that the scheduler would start
    print("Celery scheduler would start here. In production, run: celery -A app.tasks.scheduler worker --beat --loglevel=info")