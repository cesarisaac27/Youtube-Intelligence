from ..crud.videos_repository import get_videos_by_channel_id,save_video_AI_response, save_video, save_statistics, get_video_overview
from ..schemas.video import VideoListResponse, VideoSummary
from ..crud.channels_repository import get_channel_by_id
from ..services.video_api_services import fetch_channel_videos, fetch_video_stats
from ..services.video_normalizer import normalize_video
from ..services.AI_video_service import generate_video_AI_analysis
from datetime import datetime
from fastapi import HTTPException
from typing import List
from urllib.parse import urlparse, parse_qs


def get_channel_videos(channel_id: str) -> VideoListResponse:
    """
    get videos associated to channel from DB
    """

    #retrieve videos using channel id from db
    videos_data = get_videos_by_channel_id(channel_id)

    videos = [
        VideoSummary(
            id=v["id"],
            video_id=v["video_id"],
            title=v["title"],
            description=v.get("description"),
            published_at=v.get("published_at"),
            duration=v.get("duration"),
            thumbnail_url=v.get("thumbnail_url"),
            views=v.get("views"),
            likes=v.get("likes"),
            engagement_rate=v.get("engagement_rate")
        )
        for v in videos_data
    ]

    return VideoListResponse(
        
        channel_id=channel_id,
        total=len(videos),
        videos=videos
    )



def calculate_engagement(stats: dict) -> float:

    """
    Calculate video engagement rate
    """
    views = stats.get("views", 0)
    likes = stats.get("likes", 0)
    comments = stats.get("comments", 0)

    if views == 0:
        return 0.0

    return round(((likes + comments) / views) * 100, 2)



def process_top_videos(channel_id: str):

    """
    extract related channel videos from api 
    process every video 
    save top videos
    save stadistics

    """

    channel = get_channel_by_id(channel_id)
    if not channel:
        return None

    #max_results = 50

    videos = fetch_channel_videos(channel["playlist_id"])
    

    response_videos = []

    for video in videos:
        normalized = normalize_video(video, channel["id"])

        video_db_id = save_video(normalized["video"])

        #calculate engagement
        engagement = calculate_engagement(normalized["stats"])

        stats_data = {
            "video_id": video_db_id,
            "views": normalized["stats"]["views"],
            "likes": normalized["stats"]["likes"],
            "comments": normalized["stats"]["comments"],
            "engagement_rate": engagement,
            "snapshot_at": datetime.utcnow()
        }

        save_statistics(stats_data)

        response_videos.append({
            "title": normalized["video"]["title"],
            "views": stats_data["views"],
            "likes": stats_data["likes"],
            "comments": stats_data["comments"]
        })

    return {
        "channel": channel["name"],
        "total_videos": len(response_videos),
        "videos": response_videos
    }


def generate_video_AI_response(internalVideoId: str):

    """
    Generate a video AI resume using internal video id
    request to model
    """


    # retrieve channel info from database (by internal id)
    videoInternalInfo = get_video_overview(internalVideoId)

    if not videoInternalInfo:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # generate AI overview for video (service expects a dict)
    generatedAIResponse = generate_video_AI_analysis(videoInternalInfo)

    if "error" in generatedAIResponse:
        raise HTTPException(status_code=502, detail=generatedAIResponse["error"])
    
    if "raw_response" in generatedAIResponse:
        raw = generatedAIResponse["raw_response"]
        raise HTTPException(
            status_code=422,
            detail={
                "message": "AI returned invalid JSON",
                "raw_preview": raw[:1000] if isinstance(raw, str) else str(raw)[:1000],
            },
        )
    
    # persist analysis in DB (channel_id column = internal id FK)
    save_video_AI_response(int(internalVideoId), generatedAIResponse)

    return generatedAIResponse



def refresh_all_videos_stats(videoList: list) -> List[dict]:
    """
    Refresh stats for all videos in a list
    Returns a list of updated stats
    """
    updated_stats = []

    for video in videoList.videos:  
        stats = fetch_video_stats(video.id, video.video_id)
        updated_stats.append(stats)

    return updated_stats




def get_video_id_parsing_url(url: str):
    """
    Extracts YouTube video ID from different URL formats.
    """

    try:
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed_url = urlparse(url)

        # Case 1: youtube.com/watch?v=VIDEO_ID
        if "youtube.com" in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)

            if "v" in query_params:
                return query_params["v"][0]

            # Case 2: /shorts/VIDEO_ID
            if "/shorts/" in parsed_url.path:
                return parsed_url.path.split("/shorts/")[1].split("/")[0]

            # Case 3: /embed/VIDEO_ID
            if "/embed/" in parsed_url.path:
                return parsed_url.path.split("/embed/")[1].split("/")[0]

        # Case 4: youtu.be/VIDEO_ID
        if "youtu.be" in parsed_url.netloc:
            return parsed_url.path.lstrip("/")

        return None

    except Exception:
        return None






