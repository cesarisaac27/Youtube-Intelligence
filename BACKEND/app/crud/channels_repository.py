from app.database import get_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

def get_channel_by_id(channelId: str):

    """
    retrieve channel info by internal id
    """
    
    #import connection
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #create query
    query = """
            SELECT 
                ID,
                CHANNEL_ID,
                NAME,
                DESCRIPTION,
                SUBSCRIBERS,
                TOTAL_VIEWS,
                TOTAL_VIDEOS,
                THUMBNAIL_URL,
                PUBLISHED_AT,
                PLAYLIST_ID
                
            FROM 
                CHANNELS
            WHERE
                ID = %(channel_id)s
            """

    #build bindings
    bindings = {"channel_id" : channelId}

    cursor.execute(query, bindings)

    result = cursor.fetchone()

    #close connection
    cursor.close()
    conn.close()
    
    return result


def get_channel_by_name(channelName: str):

    """
    Retrieve channel by name
    """
    
    #import connection
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #create query
    query = """
            SELECT 
                channel_id,
                name,
                description,
                subscribers,
                total_views,
                total_videos,
                thumbnail_url,
                handle,
                published_at,
                playlist_id
            FROM 
                CHANNELS
            WHERE
                NAME = %(channelNm)s
            LIMIT 1
            """

    #build bindings
    bindings = {"channelNm" : channelName}
    cursor.execute(query, bindings)

    result = cursor.fetchone()

    #close connection
    cursor.close()
    conn.close()
    
    return result

def save_channel(channel_data: dict):
    """
    Save channel into DB.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            INSERT INTO channels (
                channel_id,
                name,
                description,
                subscribers,
                total_views,
                total_videos,
                thumbnail_url,
                handle,
                published_at,
                playlist_id
            ) VALUES (
                %(channel_id)s,
                %(name)s,
                %(description)s,
                %(subscribers)s,
                %(total_views)s,
                %(total_videos)s,
                %(thumbnail_url)s,
                %(handle)s,
                %(published_at)s,
                %(playlist_id)s
            )
            ON CONFLICT (channel_id) DO UPDATE SET  -- avoids duplicated channel
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            subscribers = EXCLUDED.subscribers,
            total_views = EXCLUDED.total_views,
            total_videos = EXCLUDED.total_videos,
            handle = EXCLUDED.handle,
            thumbnail_url = EXCLUDED.thumbnail_url,
            playlist_id = EXCLUDED.playlist_id,
            updated_at = NOW()
            RETURNING id;
        """

    # Datetime normalization with postgres
    if isinstance(channel_data.get("published_at"), datetime):
        channel_data["published_at"] = channel_data["published_at"].isoformat()

    cursor.execute(query, channel_data)
    result = cursor.fetchone()
    
    if result:
        resId = result[0]
    else:
        # fallback: buscar el id existente
        cursor.execute(
            "SELECT id FROM channels WHERE channel_id = %(channel_id)s",
            {"channel_id": channel_data["channel_id"]}
        )
        resId = cursor.fetchone()[0]
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return resId


def get_all_channels():
    """
    Retrieve all saved channels
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            id,
            channel_id,
            name,
            description,
            subscribers,
            total_videos,
            total_views,
            thumbnail_url,
            handle,
            published_at,
            playlist_id
        FROM
            channels
        ORDER BY name;
        """
    
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def delete_channel(id: str):
    """
    Delete selected channel by internal channel id
    """

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
            DELETE
            FROM
                channels
            WHERE 
                id = %(id)s
            RETURNING name;
        """
    
        bindings = {"id" : id}
        cursor.execute(query, bindings)

        deletedChannel = cursor.fetchone()
        
        if not deletedChannel:
            return {"error": "Channel not found"}
        
        conn.commit()

        return {"Message": f"Channel '{deletedChannel['name']}' deleted succesfully"}
    
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        cursor.close()
        conn.close()


def save_channel_AI_response(internal_channel_id: int, analysis: dict) -> None:
    """
    Inserts an AI-generated analysis into the channel_ai_responses table.

    Args:
        internal_channel_id: Primary key (id) of the channel in the channels table (FK).
        analysis: AI analysis data: channel_summary, creator_profile, target_audience,
                  content_style, main_topics, generated_at.
    """
    conn = get_connection()
    cursor = conn.cursor()

    generated_at = analysis.get("generated_at")
    if isinstance(generated_at, datetime):
        generated_at = generated_at.isoformat()

    main_topics = analysis.get("main_topics")
    if isinstance(main_topics, list):
        main_topics = json.dumps(main_topics)

    query = """
        INSERT INTO channel_ai_responses (
            channel_id,
            channel_summary,
            creator_profile,
            target_audience,
            content_style,
            main_topics,
            generated_at
        ) VALUES (
            %(channel_id)s,
            %(channel_summary)s,
            %(creator_profile)s,
            %(target_audience)s,
            %(content_style)s,
            %(main_topics)s,
            %(generated_at)s
        );
    """
    bindings = {
        "channel_id": internal_channel_id,
        "channel_summary": analysis.get("channel_summary"),
        "creator_profile": analysis.get("creator_profile"),
        "target_audience": analysis.get("target_audience"),
        "content_style": analysis.get("content_style"),
        "main_topics": main_topics,
        "generated_at": generated_at,
    }
    
    cursor.execute(query, bindings)
    conn.commit()
    cursor.close()
    conn.close()


def get_channel_existing_AI_overview(internalChannelID: str):

    """
    retrieve existing AI overview about channel stored in DB
    """

    #import connection
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #create query
    query = """
            SELECT 
                channel_id,
                channel_summary,
                creator_profile,
                target_audience,
                content_style,
                main_topics,
                generated_at
            FROM
                channel_ai_responses
            WHERE
                channel_id = %(channel_id)s
            """

    #build bindings
    bindings = {"channel_id" : internalChannelID}

    cursor.execute(query, bindings)

    channelAIOverview = cursor.fetchone()

    if channelAIOverview:
        channelAIOverview["channel_id"] = str(channelAIOverview["channel_id"])
    
    #close connection
    cursor.close()
    conn.close()
    
    return channelAIOverview



def get_channel_by_user(channelUser: str):

    """
    retrieve existing channel overview stored in DB
    search by channelUser @
    """

    

    #import connection
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #create query
    query = """
            SELECT 
                id,
                channel_id,
                name,
                description,
                subscribers,
                total_views,
                total_videos,
                thumbnail_url,
                handle,
                published_at,
                playlist_id
            FROM
                channels
            WHERE
                handle = %(channel_user)s
            """

    #build bindings
    bindings = {"channel_user" : channelUser}

    cursor.execute(query, bindings)

    singleRow = cursor.fetchone()
    
    #close connection
    cursor.close()
    conn.close()
    
    return singleRow


