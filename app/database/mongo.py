import os
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "airpollution")

client = None
db = None
history_collection = None

async def connect_to_mongo():
    global client, db, history_collection
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        history_collection = db["city_history"]
        
        # Test the connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🔌 Disconnected from MongoDB")

def get_db():
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db

def get_history_collection():
    if history_collection is None:
        raise RuntimeError("History collection not initialized. Call connect_to_mongo() first.")
    return history_collection