from ..crud.channels_repository import get_channel_by_id, get_channel_by_name, save_channel, save_channel_AI_response, get_channel_by_user
from ..schemas.channel import ChannelSummary, ChannelInfo, ChannelMetrics, ChannelDashboard
from ..services.channel_api_services import fetch_official_channel_by_name2, fetch_official_channel_by_user
from ..services.AI_channel_service import generate_channel_AI_analysis
from fastapi import HTTPException

def get_channel_summary(channel_id: str) -> ChannelSummary | None:

    """
    Get channel info from database using internal channel id
    """

    channel = get_channel_by_id(channel_id)
    if not channel:
        return None  

    return ChannelSummary(
        channel_id=channel["channel_id"],
        name=channel["name"],
        description=channel.get("description"),
        subscribers=channel.get("subscribers"),
        total_views=channel.get("total_views"),
        total_videos=channel.get("total_videos"),
        thumbnail_url=channel.get("thumbnail_url"),
        handle=channel.get("handle"),
        published_at=channel.get("published_at"),
        playlist_id=channel.get("playlist_id")
    )


def get_channel_dashboard_by_name(channel_name: str) -> ChannelDashboard | None:
    """
    First search channel in DB if not reach youtube api
    """
    # Get channel By name in DB
    channel = get_channel_by_name(channel_name)

    if channel:
        summary = ChannelSummary(**channel)
        internalId = channel["id"]
    else:
        # If not channel in Db look using youtube api
        summary = fetch_official_channel_by_name2(channel_name)
        if not summary:
            return None
        # Insert in DB
        internalId = save_channel(summary.dict())

    # Build dashboard 
    channel_info = ChannelInfo(
        id=internalId,
        channel_id=summary.channel_id,
        name=summary.name,
        description=summary.description,
        thumbnail_url=summary.thumbnail_url,
        published_at=summary.published_at
    )
    metrics = ChannelMetrics(
        subscribers=summary.subscribers,
        total_views=summary.total_views,
        total_videos=summary.total_videos
    )

    return ChannelDashboard(
        channel=channel_info,
        metrics=metrics
    )


def generate_AI_response(internalChannelId: str):

    """
    Generate AI resume for channel using channel information from db
    """

    # retrieve channel info from database (by internal id)
    channelInternalInfo = get_channel_summary(internalChannelId)

    if not channelInternalInfo:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # generate AI overview for channel (service expects a dict)
    generatedAIResponse = generate_channel_AI_analysis(channelInternalInfo.model_dump())

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
    save_channel_AI_response(int(internalChannelId), generatedAIResponse)

    return generatedAIResponse



def get_channel_dashboard_by_user(channelUser: str) -> ChannelDashboard | None:
    """
    First search channel in DB if not reach youtube api
    """

    channelUser = channelUser.lower()
    # Get channel By name in DB
    channel = get_channel_by_user(channelUser)

    if channel:
        summary = ChannelSummary(**channel)
    else:
        # If not channel in Db look using youtube api
        summary = fetch_official_channel_by_user(channelUser)

        if not summary:
            return None
        # Insert in DB
        save_channel(summary.dict())

        channel = get_channel_by_user(channelUser)

        summary = ChannelSummary(**channel)

    # Build dashboard 
    channel_info = ChannelInfo(
        id=summary.id,
        channel_id=summary.channel_id,
        name=summary.name,
        description=summary.description,
        thumbnail_url=summary.thumbnail_url,
        published_at=summary.published_at
    )
    metrics = ChannelMetrics(
        subscribers=summary.subscribers,
        total_views=summary.total_views,
        total_videos=summary.total_videos
    )

    return ChannelDashboard(
        channel=channel_info,
        metrics=metrics
    )