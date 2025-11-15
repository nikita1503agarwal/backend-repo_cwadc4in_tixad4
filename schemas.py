"""
Database Schemas for Wing Chun Revolution (SaaS e-learning platform)

Each Pydantic model represents a MongoDB collection. Collection name is the lowercase
of the class name (e.g., User -> "user").

These schemas are used for validation and also surfaced by GET /schema for tooling.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# Users of the platform
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Unique email address")
    avatar_url: Optional[str] = Field(None, description="Profile avatar URL")
    plan: Literal["BASIC", "PREMIUM", "VIP"] = Field("BASIC", description="Active subscription tier")
    country: Optional[str] = Field(None, description="Country of residence")
    is_active: bool = Field(True, description="Whether the account is active")

# Subscription transactions/audit
class Subscription(BaseModel):
    user_id: str = Field(..., description="User identifier")
    plan: Literal["BASIC", "PREMIUM", "VIP"] = Field(..., description="Purchased plan tier")
    started_at: Optional[datetime] = Field(None, description="When subscription started")
    expires_at: Optional[datetime] = Field(None, description="When subscription ends")
    status: Literal["active", "canceled", "expired", "pending"] = Field("pending")

# Video library entries
class Video(BaseModel):
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Short description")
    url: str = Field(..., description="Streaming URL")
    duration_sec: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    level: Literal["beginner", "intermediate", "advanced"] = Field("beginner")
    topics: List[str] = Field(default_factory=list, description="Tags/topics e.g., Siu Nim Tao, Chum Kiu")
    requires_plan: Literal["BASIC", "PREMIUM", "VIP"] = Field("BASIC", description="Minimum plan required")

# Per-user video progress
class Progress(BaseModel):
    user_id: str = Field(..., description="User identifier")
    video_id: str = Field(..., description="Video identifier")
    percent: float = Field(0, ge=0, le=100, description="Completion percentage")
    last_position_sec: Optional[int] = Field(0, ge=0, description="Last playback position")

# Community forum - posts
class ForumPost(BaseModel):
    user_id: str = Field(..., description="Author user id")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Markdown/HTML content")
    topics: List[str] = Field(default_factory=list, description="Tags for the post")

# Community forum - comments
class Comment(BaseModel):
    user_id: str = Field(..., description="Commenting user id")
    post_id: str = Field(..., description="Forum post id")
    content: str = Field(..., description="Comment text")

# Live classes (events)
class LiveClass(BaseModel):
    title: str = Field(..., description="Class title")
    instructor: str = Field(..., description="Instructor name")
    starts_at: datetime = Field(..., description="Start datetime (UTC)")
    ends_at: Optional[datetime] = Field(None, description="End datetime (UTC)")
    access_plan: Literal["BASIC", "PREMIUM", "VIP"] = Field("BASIC", description="Minimum plan required")
    meeting_url: Optional[str] = Field(None, description="Video conference URL")

# Enrollment for live classes
class Enrollment(BaseModel):
    user_id: str = Field(..., description="User identifier")
    class_id: str = Field(..., description="LiveClass identifier")
    status: Literal["going", "interested", "canceled"] = Field("going")
