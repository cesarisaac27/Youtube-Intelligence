import requests
from app.core.config import settings
from app.crud.videos_repository import save_statistics, save_video, get_internalChannelId
from app.crud.channels_repository import save_channel
from app.services.channel_api_services import map_channel_to_summary
from app.services.video_normalizer import parse_iso_duration, parse_datetime
from datetime import datetime
from app.services.channel_api_services import get_channels_details
from fastapi import APIRouter, HTTPException

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
BASE_URL = "https://www.googleapis.com/youtube/v3"


def fetch_channel_videos(playlist_id: str) -> list:
    """
    1) Fetch up to 300 videos from uploads playlist
    2) Retrieve statistics for those videos
    3) Sort by view count
    4) Return top 20 most viewed
    """

    MAX_VIDEOS = 300
    TOP_RESULTS = 20
    video_ids = []
    next_page_token = None

    #using playlist from channel retrieve 300 videos
    while len(video_ids) < MAX_VIDEOS:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,  # YouTube max per request
            "pageToken": next_page_token,
            "key": YOUTUBE_API_KEY
        }

        url = f"{BASE_URL}/playlistItems"
        response = requests.get(url, params=params)
        data = response.json()

        items = data.get("items", [])
        for item in items:
            video_ids.append(item["contentDetails"]["videoId"])
            if len(video_ids) >= MAX_VIDEOS:
                break

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    if not video_ids:
        return []

    videos_data = []

    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i + 50]

        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch_ids),
            "key": YOUTUBE_API_KEY
        }

        url = f"{BASE_URL}/videos"
        response = requests.get(url, params=params)
        videos_data.extend(response.json().get("items", []))

    videos_data.sort(
        key=lambda v: int(v.get("statistics", {}).get("viewCount", 0)),
        reverse=True
    )

    return videos_data[:TOP_RESULTS]


def fetch_video_stats(internalVideoId: str, video_id: str) -> dict:
    """
    Fetch statistics for a single YouTube video

    Returns:
        {
            views: int,
            likes: int,
            engagement_rate: float
        }
    """


    params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }

    url = f"{BASE_URL}/videos"
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "Failed to fetch data from YouTube API"}

    data = response.json()
    items = data.get("items", [])

    if not items:
        return {"error": "Video not found in YouTube API"}

    stats = items[0].get("statistics", {})

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments= int(stats.get("commentCount", 0))

        
    engagement_rate = 0
    if views > 0:
        engagement_rate = round(((likes + comments) / views) * 100, 2)

    stats = {
        "video_id": internalVideoId,
        "views": views,
        "likes": likes,
        "comments" : comments,
        "engagement_rate" : engagement_rate,
        "snapshot_at": datetime.utcnow()
    }

    save_statistics(stats)

    return stats



def fetch_single_video(videoId: str):
    """
    fetch a single video using youtube video ID provided by url 
    """

    params = {
        "part": "snippet,contentDetails",
        "id": videoId,
        "key": YOUTUBE_API_KEY
    }

    url = f"{BASE_URL}/videos"
    response = requests.get(url, params=params)
    data = response.json()

    items = data.get("items", [])

    if not items:
        raise HTTPException(status_code=404, detail="Video not found")

    video_data = items[0]

    youtubeChannelId = video_data["snippet"]["channelId"]

    internalChannelId = get_internalChannelId(youtubeChannelId)

    if not internalChannelId:
        #retrieving info for channel to save new channel for video 
        channelList = get_channels_details([youtubeChannelId])
        
        if not channelList:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        channel = channelList[0]
        
        channelSummary = map_channel_to_summary(channel)
        
        #save channel and retrieve internal channel id
        internalChannelId = save_channel(channelSummary.model_dump())


    parsedDuration = parse_iso_duration(video_data["contentDetails"].get("duration"))
    parsedPublishedAt = parse_datetime(video_data["snippet"].get("publishedAt"))


    mapped_video = {
        "video_id": videoId,
        "channel_id": internalChannelId,
        "title": video_data["snippet"]["title"],
        "description": video_data["snippet"].get("description"),
        "published_at": parsedPublishedAt,
        "duration": parsedDuration,
        "thumbnail_url": video_data["snippet"]["thumbnails"]["high"]["url"],
        "category_id": video_data["snippet"].get("categoryId")
    }

    internalVideoId = save_video(mapped_video)

    fetch_video_stats(internalVideoId, videoId)

    return internalVideoId










    
