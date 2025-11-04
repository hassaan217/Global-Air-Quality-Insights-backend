Air Quality Backend (FastAPI)

Project structure
- app/
  - main.py: FastAPI app factory and entrypoint
  - routers/
    - cities.py: /city endpoint to get current AQI + weather by city name
    - ranking.py: /top10 endpoint to get top-10 cities by latest AQI snapshot
  - services/
    - waqi_service.py: WAQI API integration
    - weather_service.py: OpenWeather API integration
  - database/
    - mongo.py: Motor (MongoDB) connection helper
    - history.py: Save snapshots and compute top-10
  - models/
    - schemas.py: Pydantic response schemas
    - aqi_model.py: Optional data models
  - tasks/
    - scheduler.py: Background job for periodic fetching
- requirements.txt
- .env

Setup
1) Python 3.11+ recommended. Create and activate a virtualenv.
2) pip install -r requirements.txt
3) Copy .env and fill WAQI_TOKEN and OPENWEATHER_API_KEY, ensure MongoDB is reachable.
4) Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Environment variables (.env)
- WAQI_TOKEN: Token from https://aqicn.org/data-platform/token/
- OPENWEATHER_API_KEY: API key from https://openweathermap.org/
- MONGO_URI: Mongo connection string
- MONGO_DB: Database name
- TRACK_CITIES: Comma-separated list of cities to track
- FETCH_INTERVAL_SECONDS: Background fetch interval seconds (default 1800)

Endpoints
- GET /city?name=Lahore -> returns AQI + basic weather
- GET /top10 -> returns top-10 latest AQI by city

Notes
- The background scheduler starts on app startup and runs forever; in serverless environments disable it and run a cron process that calls tasks.scheduler.run_job_once().
- CORS is open to all origins for development; restrict as needed in production.
