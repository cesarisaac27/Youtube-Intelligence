from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChannelSummary(BaseModel):
    id: Optional[int] = None
    channel_id: str
    name: str
    description: Optional[str]
    subscribers: Optional[int]
    total_views: Optional[int]
    total_videos: Optional[int]
    thumbnail_url: Optional[str]
    handle: Optional[str]
    published_at: Optional[datetime]
    playlist_id: Optional[str]


class ChannelInfo(BaseModel):
    id: Optional[int]
    channel_id: str
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    published_at: Optional[datetime]


class ChannelMetrics(BaseModel):
    subscribers: Optional[int]
    total_views: Optional[int]
    total_videos: Optional[int]


class ChannelDashboard(BaseModel):
    channel: ChannelInfo
    metrics: ChannelMetrics


class ChannelListItem(BaseModel):
    id: int
    channel_id: str
    name: str
    description: Optional[str]
    subscribers: Optional[int]
    total_views: Optional[int]
    total_videos: Optional[int]
    thumbnail_url: Optional[str]
    handle: Optional[str]
    published_at: Optional[datetime]
    playlist_id: Optional[str]

class ChannelAIAnalysis(BaseModel):
    channel_id: str
    channel_summary: Optional[str]
    creator_profile: Optional[str]
    target_audience: Optional[str]
    content_style: Optional[str]
    main_topics: Optional[List[str]]
    generated_at: Optional[datetime]