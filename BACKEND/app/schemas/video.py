from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

"""
Class to normalize the response for channel videos
"""


class VideoSummary(BaseModel):
    id: int
    video_id: str
    title: str
    description: Optional[str]
    published_at: Optional[datetime]
    duration: Optional[int]
    thumbnail_url: Optional[str]
    views: Optional[int]
    likes: Optional[int]
    engagement_rate: Optional[float]


class VideoListResponse(BaseModel):
    channel_id: str
    total: int
    videos: List[VideoSummary]

class VideoStats(BaseModel):
    video_id: int
    views: int
    likes: int
    comments: int
    engagement_rate: Optional[float] = None
    snapshot_at: Optional[datetime] = None

class TopVideosResponse(BaseModel):
    channel: str
    total_videos: int
    videos: list[dict]


class VideoOverviewResponse(BaseModel):
    id: int
    channel_id: int
    video_id: str
    title: str
    description: Optional[str]
    published_at: Optional[datetime]
    duration: Optional[int]
    thumbnail_url: Optional[str]
    views: Optional[int]
    likes: Optional[int]
    comments: Optional[int]
    engagement_rate: Optional[float]
    last_snapshot: Optional[datetime]


class VideoAIAnalysis(BaseModel):
    video_id: str
    video_summary: Optional[str]
    hook_analysis: Optional[str]
    sentiment: Optional[str]
    content_category: Optional[str]
    main_topics: Optional[List[str]]
    engagement_insight: Optional[str]
    generated_at: Optional[datetime]
    updated_at: Optional[datetime]
     
