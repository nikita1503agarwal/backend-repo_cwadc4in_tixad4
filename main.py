import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User, Subscription, Video, Progress, ForumPost, Comment, LiveClass, Enrollment

app = FastAPI(title="Wing Chun Revolution API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Wing Chun Revolution backend is running"}

# Utility to coerce ObjectId to str in responses

def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

# Health/test endpoints
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Minimal API for initial app demo: list videos, track progress, simple forum list/create

class CreateVideo(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    duration_sec: Optional[int] = None
    level: str = "beginner"
    topics: List[str] = []
    requires_plan: str = "BASIC"

class CreateProgress(BaseModel):
    user_id: str
    video_id: str
    percent: float = 0
    last_position_sec: Optional[int] = 0

class CreateForumPost(BaseModel):
    user_id: str
    title: str
    content: str
    topics: List[str] = []

@app.get("/api/videos")
def list_videos(limit: int = 50):
    docs = get_documents("video", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/videos")
def create_video(payload: CreateVideo):
    vid = Video(**payload.model_dump())
    new_id = create_document("video", vid)
    return {"id": new_id}

@app.get("/api/progress/{user_id}")
def get_user_progress(user_id: str, limit: int = 200):
    docs = get_documents("progress", {"user_id": user_id}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/progress")
def upsert_progress(p: CreateProgress):
    # naive upsert by (user_id, video_id)
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    coll = db["progress"]
    existing = coll.find_one({"user_id": p.user_id, "video_id": p.video_id})
    data = Progress(**p.model_dump()).model_dump()
    from datetime import datetime, timezone
    data["updated_at"] = datetime.now(timezone.utc)
    if existing:
        coll.update_one({"_id": existing["_id"]}, {"$set": data})
        return {"id": str(existing["_id"]) }
    else:
        from datetime import datetime, timezone
        data["created_at"] = datetime.now(timezone.utc)
        result = coll.insert_one(data)
        return {"id": str(result.inserted_id)}

@app.get("/api/forum/posts")
def list_posts(limit: int = 50):
    docs = get_documents("forumpost", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/forum/posts")
def create_post(p: CreateForumPost):
    post = ForumPost(**p.model_dump())
    new_id = create_document("forumpost", post)
    return {"id": new_id}

# Simple schema endpoint for tooling
@app.get("/schema")
def get_schema():
    from inspect import getmembers, isclass
    import schemas as sch
    models = [m for name, m in getmembers(sch) if isclass(m) and issubclass(m, BaseModel)]
    return {m.__name__.lower(): m.model_json_schema() for m in models}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
