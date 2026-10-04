from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from urllib.parse import urlparse, parse_qs
import os
import re
import requests

from ..database.database import get_db
from ..database.models import SocialPost


router = APIRouter(
    prefix="/api",
    tags=["Post Analyzer"]
)


class PostURLRequest(BaseModel):
    url: str


# ============================================================
# PLATFORM DETECTION
# ============================================================

def detect_platform(url):
    domain = urlparse(url).netloc.lower()

    if "youtube.com" in domain or "youtu.be" in domain:
        return "YouTube"

    if "tiktok.com" in domain:
        return "TikTok"

    if "instagram.com" in domain:
        return "Instagram"

    if "twitter.com" in domain or "x.com" in domain:
        return "Twitter"

    return "Unknown"


# ============================================================
# YOUTUBE VIDEO ID
# ============================================================

def extract_youtube_id(url):

    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc.lower():
        video_id = parsed.path.strip("/").split("/")[0]

        if video_id:
            return video_id

    query = parse_qs(parsed.query)

    if "v" in query:
        return query["v"][0]

    match = re.search(
        r"/shorts/([^/?]+)",
        parsed.path
    )

    if match:
        return match.group(1)

    match = re.search(
        r"/embed/([^/?]+)",
        parsed.path
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# TIKTOK VIDEO ID
# ============================================================

def extract_tiktok_id(url):

    parsed = urlparse(url)

    match = re.search(
        r"/video/(\d+)",
        parsed.path
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# INSTAGRAM POST ID
# ============================================================

def extract_instagram_id(url):

    parsed = urlparse(url)

    match = re.search(
        r"/(?:p|reel|reels|tv)/([^/?]+)",
        parsed.path
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# TWITTER / X POST ID
# ============================================================

def extract_twitter_id(url):

    parsed = urlparse(url)

    match = re.search(
        r"/status/(\d+)",
        parsed.path
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# YOUTUBE API
# ============================================================

def get_youtube_metrics(video_id):

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "YouTube API key is not configured. "
                "Add YOUTUBE_API_KEY to your .env file."
            )
        )

    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics",
                "id": video_id,
                "key": api_key
            },
            timeout=15
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not connect to YouTube API: {str(e)}"
        )

    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = (
                error_data
                .get("error", {})
                .get("message", "Unknown YouTube API error.")
            )
        except Exception:
            error_message = response.text

        raise HTTPException(
            status_code=502,
            detail=f"YouTube API error: {error_message}"
        )

    data = response.json()

    if not data.get("items"):
        raise HTTPException(
            status_code=404,
            detail=(
                f"YouTube video '{video_id}' was not found, "
                "is unavailable, or cannot be accessed."
            )
        )

    video = data["items"][0]

    statistics = video.get("statistics", {})
    snippet = video.get("snippet", {})

    return {
        "views": int(statistics.get("viewCount", 0)),
        "likes": int(statistics.get("likeCount", 0)),
        "shares": 0,
        "comments": int(statistics.get("commentCount", 0)),
        "title": snippet.get("title"),
        "published_at": snippet.get("publishedAt")
    }

# ============================================================
# INSTAGRAM API
# ============================================================

def normalize_instagram_url(url):
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")

    return f"https://www.instagram.com{path}/"


def get_instagram_metrics(url):
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not access_token:
        return {
            "status": "not_configured",
            "message": (
                "Instagram API access is not configured."
            )
        }

    normalized_url = normalize_instagram_url(url)

    try:
        response = requests.get(
            "https://graph.instagram.com/me/media",
            params={
                "fields": (
                    "id,"
                    "caption,"
                    "media_type,"
                    "permalink,"
                    "timestamp,"
                    "like_count,"
                    "comments_count"
                ),
                "limit": 50,
                "access_token": access_token
            },
            timeout=15
        )

    except requests.RequestException:
        return {
            "status": "not_accessible",
            "message": (
                "Instagram could not be reached. "
                "Please try again later."
            )
        }

    if response.status_code != 200:
        return {
            "status": "not_accessible",
            "message": (
                "This Instagram post could not be accessed "
                "through the connected Instagram API."
            )
        }

    data = response.json()

    for media in data.get("data", []):

        permalink = media.get("permalink")

        if not permalink:
            continue

        if normalize_instagram_url(permalink) == normalized_url:

            return {
                "status": "accessible",
                "views": 0,
                "likes": int(
                    media.get("like_count", 0) or 0
                ),
                "shares": 0,
                "comments": int(
                    media.get("comments_count", 0) or 0
                ),
                "title": media.get("caption"),
                "published_at": media.get("timestamp"),
                "media_id": media.get("id"),
                "media_type": media.get("media_type")
            }

    return {
        "status": "not_accessible",
        "message": (
            "This Instagram post is valid and public, "
            "but its engagement metrics are not available "
            "through the connected Instagram API."
        )
    }
# ============================================================
# TIKTOK API
# ============================================================

def get_tiktok_metrics(video_id):

    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

    if not access_token:
        raise HTTPException(
            status_code=503,
            detail=(
                "TikTok access token is not configured. "
                "Add TIKTOK_ACCESS_TOKEN to your .env file."
            )
        )

    response = requests.post(
        "https://open.tiktokapis.com/v2/video/query/",
        params={
            "fields": (
                "id,title,like_count,comment_count,"
                "share_count,view_count"
            )
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={
            "filters": {
                "video_ids": [video_id]
            }
        },
        timeout=15
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="TikTok API request failed."
        )

    data = response.json()

    videos = data.get(
        "data", {}
    ).get(
        "videos",
        []
    )

    if not videos:
        raise HTTPException(
            status_code=404,
            detail="TikTok video was not found or is not accessible."
        )

    video = videos[0]

    return {
        "views": int(video.get("view_count", 0)),
        "likes": int(video.get("like_count", 0)),
        "shares": int(video.get("share_count", 0)),
        "comments": int(video.get("comment_count", 0)),
        "title": video.get("title"),
        "published_at": video.get("create_time")
    }


# ============================================================
# METRIC CALCULATION
# ============================================================

def calculate_metrics(
    views,
    likes,
    shares,
    comments
):

    if views <= 0:

        return {
            "engagement_rate": 0,
            "share_rate": 0,
            "comment_rate": 0,
            "like_rate": 0,
            "viral_coefficient": 0,
            "virality_score": 0
        }

    engagement_rate = (
        (likes + shares + comments)
        / views
    ) * 100

    share_rate = (
        shares / views
    ) * 100

    comment_rate = (
        comments / views
    ) * 100

    like_rate = (
        likes / views
    ) * 100

    viral_coefficient = (
        0.60 * (shares / views)
        + 0.20 * (comments / views)
        + 0.20 * (likes / views)
    )

    virality_score = (
        viral_coefficient * 100
    )

    return {
        "engagement_rate": round(
            engagement_rate,
            2
        ),
        "share_rate": round(
            share_rate,
            2
        ),
        "comment_rate": round(
            comment_rate,
            2
        ),
        "like_rate": round(
            like_rate,
            2
        ),
        "viral_coefficient": round(
            viral_coefficient,
            4
        ),
        "virality_score": round(
            virality_score,
            2
        )
    }


# ============================================================
# ENGAGEMENT LEVEL
# ============================================================

def get_engagement_level(rate):

    if rate >= 20:
        return "High"

    if rate >= 10:
        return "Medium"

    return "Low"


# ============================================================
# POST ANALYZER
# ============================================================

@router.post("/analyze-post")
def analyze_post(
    request: PostURLRequest,
    db: Session = Depends(get_db)
):

    url = request.url.strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a post URL."
        )

    platform = detect_platform(url)

    if platform == "Unknown":
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported platform. "
                "Currently supported: "
                "YouTube, TikTok and Instagram."
            )
        )

    # --------------------------------------------------------
    # EXTRACT POST ID
    # --------------------------------------------------------

    if platform == "YouTube":

        post_id = extract_youtube_id(url)

    elif platform == "TikTok":

        post_id = extract_tiktok_id(url)

    elif platform == "Instagram":

        post_id = extract_instagram_id(url)

    elif platform == "Twitter":

        post_id = extract_twitter_id(url)

    else:

        post_id = None

    if not post_id:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not extract the {platform} post ID "
                "from the provided URL."
            )
        )

    # --------------------------------------------------------
    # FETCH METRICS
    # --------------------------------------------------------

    if platform == "YouTube":

        metrics_data = get_youtube_metrics(
            post_id
        )

    elif platform == "TikTok":

        metrics_data = get_tiktok_metrics(
            post_id
        )

    elif platform == "Instagram":

        metrics_data = get_instagram_metrics(url)

        if metrics_data.get("status") != "accessible":
            return {
                "status": metrics_data.get(
                    "status",
                    "not_accessible"
                ),
                "post": {
                    "url": url,
                    "platform": "Instagram",
                    "post_id": post_id
                },
                "message": metrics_data.get(
                    "message",
                    "Instagram metrics are not available."
                )
            }

    else:

        raise HTTPException(
            status_code=501,
            detail=(
                f"Automatic metric extraction for "
                f"{platform} is not configured yet."
            )
        )

    views = metrics_data["views"]
    likes = metrics_data["likes"]
    shares = metrics_data["shares"]
    comments = metrics_data["comments"]

    # --------------------------------------------------------
    # CALCULATED METRICS
    # --------------------------------------------------------

    metrics = calculate_metrics(
        views,
        likes,
        shares,
        comments
    )

    engagement_level = get_engagement_level(
        metrics["engagement_rate"]
    )

    anomaly = (
        likes > views
        or shares > views
        or comments > views
    )

    # --------------------------------------------------------
    # SOCIALPULSE COMPARISON
    # --------------------------------------------------------

    query = db.query(SocialPost)

    query = query.filter(
        SocialPost.platform.ilike(platform)
    )

    comparison_posts = query.all()

    engagement_values = sorted(
        post.engagement_rate
        for post in comparison_posts
        if post.engagement_rate is not None
    )

    virality_values = sorted(
        post.virality_score
        for post in comparison_posts
        if post.virality_score is not None
    )

    if engagement_values:

        middle = len(
            engagement_values
        ) // 2

        if len(engagement_values) % 2:

            median_engagement = (
                engagement_values[middle]
            )

        else:

            median_engagement = (
                engagement_values[middle - 1]
                + engagement_values[middle]
            ) / 2

    else:

        median_engagement = 0

    if virality_values:

        middle = len(
            virality_values
        ) // 2

        if len(virality_values) % 2:

            median_virality = (
                virality_values[middle]
            )

        else:

            median_virality = (
                virality_values[middle - 1]
                + virality_values[middle]
            ) / 2

    else:

        median_virality = 0

    engagement_difference = (
        metrics["engagement_rate"]
        - median_engagement
    )

    virality_difference = (
        metrics["virality_score"]
        - median_virality
    )

    engagement_vs_median = (
        (
            metrics["engagement_rate"]
            / median_engagement
        ) * 100
        if median_engagement > 0
        else None
    )

    virality_vs_median = (
        (
            metrics["virality_score"]
            / median_virality
        ) * 100
        if median_virality > 0
        else None
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "status": "accessible",

        "post": {
            "url": url,
            "platform": platform,
            "post_id": post_id,
            "title": metrics_data.get("title"),
            "published_at": metrics_data.get(
                "published_at"
            )
        }, 

    "raw_metrics": {
        "views": views,
        "likes": likes,
        "shares": shares,
        "comments": comments
    },

    "calculated_metrics": metrics,

        "classification": {
            "engagement_level":
                engagement_level,
            "engagement_anomaly":
                anomaly
        },

        "comparison": {
            "comparison_posts":
                len(comparison_posts),

            "median_engagement":
                round(
                    median_engagement,
                    2
                ),

            "median_virality":
                round(
                    median_virality,
                    2
                ),

            "engagement_difference":
                round(
                    engagement_difference,
                    2
                ),

            "virality_difference":
                round(
                    virality_difference,
                    2
                ),

            "engagement_vs_median_percent":
                round(
                    engagement_vs_median,
                    2
                )
                if engagement_vs_median is not None
                else None,

            "virality_vs_median_percent":
                round(
                    virality_vs_median,
                    2
                )
                if virality_vs_median is not None
                else None
        }
    }