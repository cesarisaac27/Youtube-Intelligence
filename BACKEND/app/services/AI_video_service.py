import os
import requests
from datetime import datetime

from ..services.AI_response_normalizer import _fix_trailing_commas, _fix_missing_commas, _extract_json

AI_TOKEN = os.getenv("YOUTUBE_AI_TOKEN")
API_URL = os.getenv("API_AI_URL")
API_MODEL = os.getenv("API_AI_MODEL")

headers = {
    "Authorization": f"Bearer {AI_TOKEN}",
    "Content-Type": "application/json",
}

def generate_video_AI_analysis(videoDBInfo: dict) -> dict:
    """
    Generate an AI response for creating a resume about video 
    """

    prompt = f"""
        You are a professional YouTube video analyst.

        Analyze ONLY the information provided below.
        You MUST include ALL fields even if null.
        Do NOT assume information that is not explicitly given.
        Return ONLY this JSON structure.
        Do NOT add extra fields.
        Do NOT nest objects.
        Do NOT use markdown.
        Write everything in English.
        Keep responses concise.

        VIDEO DATA:
        Title: {videoDBInfo["title"]}
        Description: {videoDBInfo.get("description") or "No description available"}
        Views: {videoDBInfo.get("views")}
        Likes: {videoDBInfo.get("likes")}
        Comments: {videoDBInfo.get("comments")}
        Engagement rate (%): {videoDBInfo.get("engagement_rate")}
        Duration: {videoDBInfo.get("duration")}
        Published at: {videoDBInfo.get("published_at")}

        {{
        "video_summary": "Short summary of the video (max 80 words)",
        "main_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
        "sentiment": "positive, neutral, or negative",
        "hook_analysis": "Brief evaluation of how compelling the title/topic is (max 40 words)",
        "engagement_insight": "Short insight based on engagement rate and interactions (max 40 words)",
        "content_category": "content_category must be ONE of the following: Education, Entertainment, Music, Gaming, Technology,Business, Lifestyle, News, Sports, Tutorial, Documentary, Other"
        }}
    """

    payload = {
        "model": API_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
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
        return {"id": videoDBInfo["id"], "raw_response": textResponse}


    parsed["video_id"] = str(videoDBInfo["id"])
    parsed.setdefault("content_category", "Other")
    parsed.setdefault("generated_at", datetime.utcnow())
    parsed.setdefault("updated_at", datetime.utcnow())
    parsed.setdefault("video_summary", None)
    parsed.setdefault("hook_analysis", None)
    parsed.setdefault("sentiment", None)
    parsed.setdefault("main_topics", [])
    parsed.setdefault("engagement_insight", None)

    return parsed

    
