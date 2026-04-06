from fastapi import APIRouter, HTTPException
from app.services.video_service import get_channel_videos, process_top_videos, refresh_all_videos_stats
from app.services.video_api_services import fetch_video_stats, fetch_single_video
from app.services.video_normalizer import  normalize_video_overview, normalize_stadistics_snapshots
from app.schemas.video import VideoListResponse, TopVideosResponse, VideoOverviewResponse, VideoStats, VideoAIAnalysis
from app.crud.videos_repository import get_video_existing_AI_overview, get_youtube_videoID, delete_video, get_video_overview, get_full_stadistics_snapshots, save_video_AI_response
from app.services.video_service import generate_video_AI_response, get_video_id_parsing_url
from typing import List

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.get("/channel/{channel_id}", response_model=VideoListResponse)
def get_videos(channel_id: str):
    """
    Retrieve channel associated videos 
    """
    response = get_channel_videos(channel_id)


    if response.total == 0:
        raise HTTPException(status_code=404, detail="No videos found")

    return response


@router.post("/{channel_id}/top", response_model=TopVideosResponse)
def fetch_top_videos(channel_id: str):
    """
    Fetch top 5 videos from YouTube, store video and statistics in DB,
    and return a summary response.
    """

    result = process_top_videos(channel_id)

    if not result:
        raise HTTPException(status_code=404, detail="Channel not found")

    return result


@router.delete("/deleteVid/{internalVideoId}")
def delete_video_endpoint(internalVideoId: str):
    """
    Endpoint to delete a video using internal ID
    """

    result = delete_video(internalVideoId)

    if "error" in result:
        raise HTTPException(status_code= 404, detail= result["error"])
        
    return result


@router.get("/id/{internalVideoId}", response_model=VideoOverviewResponse)
def get_video_latest_stadistics(internalVideoId: str):
    """
    Endpoint to get a video overview using internal ID
    """

    result = get_video_overview(internalVideoId)
    normalized = normalize_video_overview(result)

    if not normalized:
        raise HTTPException(status_code=404, detail="Video not found")

    return normalized


@router.get("/{internalVideoId}/fullStats", response_model=list[VideoStats])
def get_video_stadistics(internalVideoId: str):
    """
    Endpoint to get a all stadistics over the time 
    snapshots using video internal ID
    """

    result = get_full_stadistics_snapshots(internalVideoId)
    normalized = normalize_stadistics_snapshots(result)

    if not normalized:
        raise HTTPException(status_code=404, detail="Video not found")

    return normalized



@router.post("/{internalVideoId}/generate-ai-analysis", response_model=VideoAIAnalysis)
def generate_video_AI_resume(internalVideoId: str):
    """
    Endpoint to generate Video AI analysis using internal video id 
    retrieve info from video db 
    Generate payload 
    receive AI Response
    """

    generatedAIResponse = generate_video_AI_response(internalVideoId)

    if not generatedAIResponse:
        raise HTTPException(status_code=404, detail="Video AI response not generated")

    return generatedAIResponse



@router.get("/{internalVideoId}/retrieve-ai-analysis", response_model=VideoAIAnalysis)
def retrieve_video_AI_resume(internalVideoId: str):
    """
    Endpoint to retrieve existing Video AI analysis using internal video id 
    retrieve info from video db AI
    if not existing
    Generate payload 
    receive AI Response
    """
    #retrieve video AI generated info if exist
    currentAIResponse = get_video_existing_AI_overview(internalVideoId)

    if currentAIResponse:
        return currentAIResponse
    

    #if not exist generate AI overview for video
    aiResponse = generate_video_AI_response(internalVideoId)

    if not aiResponse:
        raise HTTPException(status_code=404, detail="AI video response not generated correctly")


    return aiResponse


@router.post("/{internalVideoId}/refreshStats", response_model=VideoStats)
def refresh_video_stats(internalVideoId: str):
    """
    Endpoint to fetch existing Video stats using internal video id 
    
    """

    res = get_youtube_videoID(internalVideoId)
    
    youtubeVideoId = res["video_id"]

    #Fetch new video stats 
    fetch = fetch_video_stats(internalVideoId, youtubeVideoId)

    if not fetch:
        raise HTTPException(status_code=404, detail="Error retrieving stats")

    return fetch



@router.post("/{internalChannelId}/refreshAllStats", response_model=List[VideoStats])
def refresh_all_video_stats_for_channel(internalChannelId: str):
    """
    Endpoint to update/fetch existing Video stats using internal channel id for all videos
    """
    
    videos = get_channel_videos(internalChannelId)

    if not videos.videos:
        raise HTTPException(status_code=404, detail="No videos found for this channel")

    
    updated_stats = refresh_all_videos_stats(videos)

    return updated_stats


@router.post("/fetchSingleVideo", response_model=VideoOverviewResponse)
def fetch_single_video_by_url(videoURL: str):
    """
    Endpoint to fetch single Video using video url
    """

    videoId = get_video_id_parsing_url(videoURL)

    if not videoId:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    
    internalVideoId = fetch_single_video(videoId)

    if not internalVideoId:
        raise HTTPException(status_code=400, detail="failure saving video")
    
    newVideo = get_video_overview(internalVideoId)

    return newVideo