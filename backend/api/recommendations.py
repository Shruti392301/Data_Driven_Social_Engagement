from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.database import get_db
from ..database.models import SocialPost


router = APIRouter(
    prefix="/api",
    tags=["Recommendations"]
)


@router.get("/recommendations")
def get_recommendations(
    platform: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(SocialPost)

    # Platform filter
    if platform and platform.lower() != "all":
        query = query.filter(
            func.lower(SocialPost.platform) == platform.lower()
        )

    # Region filter
    if region and region.lower() != "all":
        query = query.filter(
            func.lower(SocialPost.region) == region.lower()
        )

    posts = query.all()

    if not posts:
        return []

    groups = {}

    for post in posts:

        key = (
            post.content_type,
            post.hashtag
        )

        if key not in groups:

            groups[key] = {
                "content_type": post.content_type,
                "hashtag": post.hashtag,
                "virality": [],
                "engagement": [],
                "shares": []
            }

        groups[key]["virality"].append(
            post.virality_score
        )

        groups[key]["engagement"].append(
            post.engagement_rate
        )

        groups[key]["shares"].append(
            post.shares
        )

    recommendations = []

    for key, group in groups.items():

        post_count = len(group["virality"])

        if post_count < 5:
            continue

        recommendations.append(
            {
                "content_type": group["content_type"],
                "hashtag": group["hashtag"],
                "posts": post_count,
                "median_virality": round(
                    float(
                        __import__("statistics").median(
                            group["virality"]
                        )
                    ),
                    2
                ),
                "median_engagement": round(
                    float(
                        __import__("statistics").median(
                            group["engagement"]
                        )
                    ),
                    2
                ),
                "avg_shares": round(
                    sum(group["shares"]) / len(group["shares"]),
                    2
                )
            }
        )

    recommendations.sort(
        key=lambda x: (
            x["median_virality"],
            x["median_engagement"]
        ),
        reverse=True
    )

    return recommendations[:10]