from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cities, ranking, global_stats
from app.database.mongo import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Global Air Quality API", version="1.0.0")

# CORS (allow local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cities.router, prefix="/city", tags=["cities"])
app.include_router(ranking.router, prefix="/cities", tags=["ranking"])
app.include_router(global_stats.router, prefix="/global", tags=["Global AQI"])

# DB lifecycle
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

@app.get("/")
async def root():
    return {"message": "Global Air Quality Insights API"}

if __name__ == "__main__":
    import uvicorn, os
    uvicorn.run("app.main:app", host=os.getenv("APP_HOST", "0.0.0.0"), port=int(os.getenv("APP_PORT", 8000)), reload=True)
