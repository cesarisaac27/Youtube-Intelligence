from app.database import get_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

def get_videos_by_channel_id(channel_id: str):

    """
    retrieve videos using internal channel id
    """

    #import connection
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)    
    
    query = """
        SELECT
            v.id,
            v.video_id,
            v.title,
            v.description,
            v.published_at,
            v.duration,
            v.thumbnail_url,
            v.category_id,
            s.views,
            s.likes,
            s.engagement_rate
        FROM (
            SELECT
                s.*,
                ROW_NUMBER() OVER (
            PARTITION BY s.video_id
            ORDER BY s.snapshot_at DESC
            ) rn
        FROM video_stats s
            ) s
        JOIN videos v ON v.id = s.video_id
        JOIN channels c ON c.id = v.channel_id
        WHERE c.id = %(channel_id)s
        AND s.rn = 1
        ORDER BY v.published_at DESC;

    """
    
    bindings = {"channel_id": channel_id}

    cursor.execute(query, bindings)
    resultList = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultList

def save_video(video_data: dict) -> int:

    """
    Save video retrieved by api
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        INSERT INTO videos (
            video_id,
            channel_id,
            title,
            description,
            published_at,
            duration,
            thumbnail_url,
            category_id
        )
        VALUES (
            %(video_id)s,
            %(channel_id)s, 
            %(title)s, 
            %(description)s, 
            %(published_at)s, 
            %(duration)s, 
            %(thumbnail_url)s, 
            %(category_id)s
            )
        ON CONFLICT (video_id) DO NOTHING 
        RETURNING id;
    """

    # Datetime normalization with postgres
    if isinstance(video_data.get("published_at"), datetime):
        video_data["published_at"] = video_data["published_at"].isoformat()

    cursor.execute(query, video_data)  
    resultRow = cursor.fetchone()

    if resultRow:
        video_id = resultRow["id"]

    else:
        #if video found search video using id
        cursor.execute(
            "SELECT id FROM videos WHERE video_id = %(video_id)s",
            {"video_id": video_data["video_id"]}
        )
        video_id = cursor.fetchone()["id"]
    

    conn.commit()
    cursor.close()
    conn.close()

    return video_id



def save_statistics(stats_data: dict):

    """
    Save video stadistics in db
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        INSERT INTO video_stats (
            video_id,
            views,
            likes,
            comments,
            engagement_rate,
            snapshot_at
        )
        VALUES (
            %(video_id)s,
            %(views)s,
            %(likes)s,
            %(comments)s,
            %(engagement_rate)s,
            %(snapshot_at)s
        )
        ON CONFLICT (video_id, snapshot_at) DO NOTHING;

    """

    if isinstance(stats_data.get("snapshot_at"), datetime):
        stats_data["snapshot_at"] = stats_data["snapshot_at"].isoformat()
 
    cursor.execute(query, stats_data)

    conn.commit()
    cursor.close()
    conn.close()


def delete_video(id: str):
    """
    Delete selected video by internal video id
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
            DELETE
            FROM
                videos
            WHERE 
                id = %(id)s
            RETURNING title;
        """
    
        bindings = {"id" : id}
        cursor.execute(query, bindings)

        deletedVideo = cursor.fetchone()
        
        if not deletedVideo:
            return {"error": "Channel not found"}
        
        conn.commit()

        return {"Message": f"Video '{deletedVideo['title']}' deleted succesfully"}
    
    except Exception as e:
        conn.rollback
        return {"error": str(e)}
    
    finally:
        cursor.close()
        conn.close()

    

def get_video_overview(internalVideoId: str):

    """
    Endpoint to get a video and its stadistics using internal ID
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            v.id,
            v.video_id,
            v.channel_id,
            v.title,
            v.description,
            v.published_at,
            v.duration,
            v.thumbnail_url,
            vs.views,
            vs.likes,
            vs.comments,
            vs.engagement_rate,
            vs.snapshot_at AS last_snapshot
        FROM
            videos v
        LEFT JOIN video_stats vs
            ON vs.video_id = v.id
        WHERE
            v.id = %(internalVId)s
        ORDER BY vs.snapshot_at DESC
        LIMIT 1;
    """

    bindings = {"internalVId": internalVideoId}

    cursor.execute(query, bindings)
    resultRow = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultRow


def get_full_stadistics_snapshots(internalVideoId: str):
    """
    Get a all stadistics over the time 
    snapshots retrieved using video internal ID
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            vs.video_id,
            vs.views,
            vs.likes,
            vs.comments,
            vs.engagement_rate,
            vs.snapshot_at
        FROM
            video_stats vs
        WHERE
            vs.video_id = %(internalVideoId)s
        ORDER BY vs.snapshot_at DESC;
    """

    bindings = {"internalVideoId": internalVideoId}

    cursor.execute(query, bindings)
    resultList = cursor.fetchall()
    cursor.close()
    conn.close()

    return resultList


def save_video_AI_response(internalVideId: int, videoDbInfo: dict):

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        INSERT INTO video_ai_responses (
            video_id,
            video_summary,
            hook_analysis,
            sentiment,
            content_category,
            main_topics,
            engagement_insight,
            generated_at,
            updated_at
        )
        VALUES (
            %(video_id)s,
            %(video_summary)s,
            %(hook_analysis)s,
            %(sentiment)s,
            %(content_category)s,
            %(main_topics)s,
            %(engagement_insight)s,
            %(generated_at)s,
            %(updated_at)s
        )
        ON CONFLICT (video_id)
        DO UPDATE SET
            video_summary = EXCLUDED.video_summary,
            hook_analysis = EXCLUDED.hook_analysis,
            sentiment = EXCLUDED.sentiment,
            content_category = EXCLUDED.content_category,
            main_topics = EXCLUDED.main_topics,
            engagement_insight = EXCLUDED.engagement_insight,
            updated_at = EXCLUDED.updated_at;
    """

    bindings = { 
        "video_id": internalVideId,
        "video_summary": videoDbInfo.get("video_summary"),
        "hook_analysis": videoDbInfo.get("hook_analysis"),
        "sentiment": videoDbInfo.get("sentiment"),
        "content_category": videoDbInfo.get("content_category"),
        "main_topics": json.dumps(videoDbInfo.get("main_topics")) if videoDbInfo.get("main_topics") else None,
        "engagement_insight": videoDbInfo.get("engagement_insight"),
        "generated_at": videoDbInfo.get("generated_at"),
        "updated_at": videoDbInfo.get("updated_at")}
    
    if isinstance(bindings.get("generated_at"), datetime):
        bindings["generated_at"] = bindings["generated_at"].isoformat()

    if isinstance(bindings.get("updated_at"), datetime):
        bindings["updated_at"] = bindings["updated_at"].isoformat()
    
    cursor.execute(query, bindings)

    conn.commit()
    cursor.close()
    conn.close()



def get_video_existing_AI_overview(internalVideoID: str):

    """
    retrieve existing AI overview about video stored in DB
    """

    #import connection
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #create query
    query = """    
        SELECT 
            video_id, 
            video_summary,
            hook_analysis, 
            sentiment, 
            content_category, 
            main_topics, 
            engagement_insight, 
            generated_at, 
            updated_at
        FROM
            video_ai_responses
        where
            video_id = %(video_id)s
        
        """

    #build bindings
    bindings = {"video_id" : internalVideoID}

    cursor.execute(query, bindings)

    videoAIOverview = cursor.fetchone()

    if videoAIOverview:
        videoAIOverview["video_id"] = str(videoAIOverview["video_id"])
    
    #close connection
    cursor.close()
    conn.close()
    
    return videoAIOverview



def get_youtube_videoID(internalVideoId: str):

    """
    Endpoint to get a video id
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            video_id
        FROM
            videos
        WHERE
            id = %(internalVId)s
    """

    bindings = {"internalVId": internalVideoId}

    cursor.execute(query, bindings)
    resultRow = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultRow


def get_internalChannelId(youtubeChannelId : str):

    """
    retrieve internal channel id ui¿sing youtube channel id
    you can use this to verify existing channels for video
    """
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
                SELECT
                    id
                from 
                    channels
                where 
                    channel_id = %(youtubeChannel)s
    """
    
    bindings = {"youtubeChannel": youtubeChannelId}

    cursor.execute(query, bindings)
    resultRow = cursor.fetchone()

    cursor.close()
    conn.close()
    
    if not resultRow:
        return None

    return resultRow["id"]



