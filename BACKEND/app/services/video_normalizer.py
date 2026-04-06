from datetime import datetime
import re

def normalize_video(video: dict, channel_db_id: int) -> dict:

    """
    Normalize video using required format
    """

    snippet = video["snippet"]
    stats = video.get("statistics", {})
    content_details = video.get("contentDetails", {})

    # Transform ISO-8601 duration to seconds
    raw_duration = content_details.get("duration")
    vid_duration = parse_iso_duration(raw_duration)


    normalized_video = {
        "video_id": video["id"],
        "channel_id": channel_db_id,
        "title": snippet["title"],
        "description": snippet.get("description"),
        "published_at": snippet.get("publishedAt"),
        "duration": vid_duration, 
        "thumbnail_url": snippet["thumbnails"]["high"]["url"],
        "category_id": snippet.get("categoryId"),
    }

    normalized_stats = {
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
    }

    return {
        "video": normalized_video,
        "stats": normalized_stats,
    }


def parse_iso_duration(duration):
    if not duration or duration == "P0D":
        return None  # live video

    pattern = re.compile(
        r'PT'
        r'(?:(\d+)H)?'
        r'(?:(\d+)M)?'
        r'(?:(\d+)S)?'
    )

    match = pattern.match(duration)
    if not match:
        return None

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds



def parse_datetime(value):
    """
    Converts a value to datetime if it is provided as a string.
    """

    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return None


def normalize_video_overview(row: dict | None) -> dict | None:
    """
    Normalizes the response from get_video_overview into a dictionary compatible
    with VideoOverviewResponse. Converts date fields and ensures numeric types
    (int/float) for statistics.
    """

    if not row:
        return None

    return {
        "id": row["id"],
        "channel_id": row["channel_id"],
        "video_id": row["video_id"],
        "title": row["title"],
        "description": row.get("description"),
        "published_at": parse_datetime(row.get("published_at")),
        "duration": row.get("duration"),
        "thumbnail_url": row.get("thumbnail_url"),
        "views": int(row["views"]) if row.get("views") is not None else None,
        "likes": int(row["likes"]) if row.get("likes") is not None else None,
        "comments": int(row["comments"]) if row.get("comments") is not None else None,
        "engagement_rate": float(row["engagement_rate"]) if row.get("engagement_rate") is not None else None,
        "last_snapshot": parse_datetime(row.get("last_snapshot")),
    }


def _normalize_one_snapshot(row: dict) -> dict:
    """
    Normalizes a statistics row into a dictionary compatible with VideoStats.
    """

    return {
        "video_id": str(row["video_id"]),
        "views": int(row["views"]) if row.get("views") is not None else None,
        "likes": int(row["likes"]) if row.get("likes") is not None else None,
        "comments": int(row["comments"]) if row.get("comments") is not None else None,
        "engagement_rate": float(row["engagement_rate"]) if row.get("engagement_rate") is not None else None,
        "snapshot_at": parse_datetime(row.get("snapshot_at")),
    }


def normalize_stadistics_snapshots(rows: list) -> list[dict]:
    """
    Normalizes the response from get_full_stadistics_snapshots (list of rows)
    into a list of dictionaries compatible with VideoStats.
    """

    if not rows:
        return []
    return [_normalize_one_snapshot(row) for row in rows]