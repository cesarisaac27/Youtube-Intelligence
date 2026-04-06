from fastapi import APIRouter, HTTPException
from app.crud.channels_repository import get_all_channels, delete_channel, get_channel_existing_AI_overview
from app.services.channel_service import get_channel_dashboard_by_user, get_channel_summary, get_channel_dashboard_by_name, generate_AI_response
from app.schemas.channel import ChannelSummary, ChannelAIAnalysis, ChannelListItem

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.get("/{channel_id}", response_model=ChannelSummary)
def get_channel(channel_id: str):
    """
    Endpoint searching channel by id
    """
    channel = get_channel_summary(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return channel


@router.get("/search/{channel_name}")
def search_channel(channel_name: str):
    """
    Endpoint searching channel by name
    """
    dashboard = get_channel_dashboard_by_name(channel_name)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Channel not found")
    return dashboard


@router.get("", response_model=list[ChannelListItem])
def list_all_channels():
    """
    Endpoint retrieve all channels saved in DB
    """
    result = get_all_channels()
    
    return result


@router.delete("/deleteChannel/{internalChannelId}")
def delete_channel_endpoint(internalChannelId: str):
    """
    Endpoint to delete a channel by internal ID
    """
    result = delete_channel(internalChannelId)

    if "error" in result:
        raise HTTPException(status_code= 404, detail= result["error"])
        

    return result



@router.post("/{internalChannelId}/ai-analysis", response_model=ChannelAIAnalysis)
def generate_channel_AI_resume(internalChannelId: str):
    """
    Endpoint to generate channel AI analysis using internal channel id 
    retrieve info from channel db 
    Generate payload 
    receive AI Response
    """

    aiResponse = generate_AI_response(internalChannelId)

    if not aiResponse:
        raise HTTPException(status_code=404, detail="AI response not generated correctly")

    return aiResponse
    


@router.get("/{internalChannelId}/existing_analysis", response_model=ChannelAIAnalysis)
def retrieve_channel_AI_resume(internalChannelId: str):
    """
    Endpoint to retrieve channel AI analysis using internal channel id 
    retrieve channel AI overview if exist, if not generate AI response
    retrieve info from channel db 
    Generate payload 
    receive AI Response
    """

    #retrieve channel AI generated info if exist
    currentAiOverview = get_channel_existing_AI_overview(internalChannelId)

    if currentAiOverview:
        return currentAiOverview
    
    #if not exist generate AI overview for channel
    aiResponse = generate_AI_response(internalChannelId)

    if not aiResponse:
        raise HTTPException(status_code=404, detail="AI response not generated correctly")

    return aiResponse



@router.get("/searchUser/{channel_user}")
def search_channel_by_user(channel_user: str):
    """
    Endpoint searching channel by user
    examples @NASA
    """
    dashboard = get_channel_dashboard_by_user(channel_user)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Channel not found")
    return dashboard





