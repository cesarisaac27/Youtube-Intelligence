import os
import requests
from datetime import datetime

from app.services.AI_response_normalizer import _extract_json

AI_TOKEN = os.getenv("YOUTUBE_AI_TOKEN")
API_URL = os.getenv("API_AI_URL")
API_MODEL = os.getenv("API_AI_MODEL")

headers = {
    "Authorization": f"Bearer {AI_TOKEN}",
    "Content-Type": "application/json",
}


def generate_channel_AI_analysis(channelDBInfo: dict) -> dict:

    """
    Generate an AI response for creating a resume about channel 
    """

    prompt = f"""
                You are a YouTube channel analyst.

                Analyze this channel INFORMATION:

                Name: {channelDBInfo["name"]}
                Description: {channelDBInfo.get("description") or "No description"}
                Subscribers: {channelDBInfo.get("subscribers")}
                Total Views: {channelDBInfo.get("total_views")}
                Total Videos: {channelDBInfo.get("total_videos")}
                Published at: {channelDBInfo.get("published_at")}

                Return ONLY this JSON structure.
                PLEASE WRITE YOUR RESPONSE IN ENGLISH ALWAYS
                DONT USE ANY OTHER LENGUAGE BUT ENGLISH
                Do NOT add extra fields.
                Do NOT nest objects.
                Do NOT use markdown.
                Keep texts concise.
                IF NOT DESCRIPTION AVAILABLE PLEASE SEARCH FOR YOUTUBE CHANNEL WITH MOST SUBSCRIBERS 
                DO NOT ASSUME INFORMATION ABOUT CHANNEL

                {{
                "channel_summary": "short paragraph (max 80 words)",
                "main_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
                "creator_profile": "short description (max 50 words)",
                "target_audience": "short description (max 40 words)",
                "content_style": "short description (max 40 words)"
                }}
            """

    
    payload = {
        "model": API_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": 0.3,
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=100)

    if response.status_code != 200:
        return {"error": f"AI service returned {response.status_code}: {response.text or response.reason}"}

    data = response.json()

    
    try:
        textResponse = (
            (data.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
        )
    except (IndexError, KeyError, TypeError):
        return {"error": f"Unexpected AI response format: {data}"}

    if not textResponse:
        return {"error": "AI returned empty content"}

    parsed = _extract_json(textResponse)
    if parsed is None:
        return {"channel_id": channelDBInfo["channel_id"], "raw_response": textResponse}

    parsed["channel_id"] = channelDBInfo["channel_id"]
    parsed.setdefault("generated_at", datetime.utcnow())
    return parsed



