import os
import requests
from datetime import datetime
from ..schemas.channel import ChannelSummary
from ..core.config import settings

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
BASE_URL = "https://www.googleapis.com/youtube/v3"

def search_channels_by_name(channel_name: str) -> list[str]:
    search_url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "q": channel_name,
        "type": "channel",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }

    resp = requests.get(search_url, params=params).json()
    
    items = resp.get("items", [])

    return [item["id"]["channelId"] for item in items]



def get_channels_details(channel_ids: list[str]) -> list[dict]:
    channels_url = f"{BASE_URL}/channels"

    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(channel_ids),
        "key": YOUTUBE_API_KEY
    }

    resp = requests.get(channels_url, params=params).json()


    if not resp:
        return None

    return resp.get("items", [])


def select_official_channel(channels: list[dict]) -> dict | None:

    if not channels:
        return None

    def get_subs_count(c):
        try:
            return int(c["statistics"]["subscriberCount"])
        except (KeyError, ValueError):
            return 0

    return max(channels, key=get_subs_count)


def map_channel_to_summary(channel: dict) -> ChannelSummary:

    snippet = channel["snippet"]
    stats = channel.get("statistics", {})

    uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

    return ChannelSummary(
        channel_id=channel["id"],
        name=snippet.get("title"),
        description=snippet.get("description"),
        subscribers=int(stats.get("subscriberCount", 0)),
        total_views=int(stats.get("viewCount", 0)),
        total_videos=int(stats.get("videoCount", 0)),
        thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
        handle=snippet.get("customUrl"),
        published_at=datetime.fromisoformat(snippet.get("publishedAt").replace("Z", "+00:00")),
        playlist_id=uploads_playlist_id
    )


def fetch_official_channel_by_name2(channel_name: str) -> ChannelSummary | None:

    channel_ids = search_channels_by_name(channel_name)

    if not channel_ids:
        return None

    channels = get_channels_details(channel_ids)

    official_channel = select_official_channel(channels)

    if not official_channel:
        return None

    
    channelSum = map_channel_to_summary(official_channel)
    return channelSum


def search_channels_by_user(channelUser: str) -> list[str]:
    search_url = f"{BASE_URL}/channels"
    params = {
        "part": "snippet",
        "forHandle": channelUser,
        "key": YOUTUBE_API_KEY
    }

    resp = requests.get(search_url, params=params).json()
    items = resp.get("items", [])

    return [item["id"] for item in items]




def fetch_official_channel_by_user(channelUser: str) -> ChannelSummary | None:


    channel_id = search_channels_by_user(channelUser)

    if not channel_id:
        return None

    channeldetail = get_channels_details(channel_id)

    oficialChannel = select_official_channel(channeldetail)

    channelSum = map_channel_to_summary(oficialChannel)
    return channelSum

