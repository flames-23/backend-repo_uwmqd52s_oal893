from typing import Any, Dict, List, Optional
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel

# Environment variables are expected to be provided by the platform
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[DATABASE_NAME]
    return _db

# Convenience alias used by instructions
_db_alias = get_db

db = get_db()


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    doc = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    filter_dict = filter_dict or {}
    cursor = db[collection_name].find(filter_dict).limit(limit)
    docs: List[Dict[str, Any]] = []
    async for d in cursor:
        d["_id"] = str(d["_id"])  # stringify ObjectId
        docs.append(d)
    return docs
