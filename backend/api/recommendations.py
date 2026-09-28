from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..database.models import SocialPost

router = APIRouter(prefix="/api", tags=["Recommendations"])


@router.get("/recommendations")
def get_recommendations(
    platform: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(SocialPost)

    if platform:
        query = query.filter(SocialPost.platform == platform)

    if region:
        query = query.filter(SocialPost.region == region)

    posts = query.all()

    if not posts:
        return []

    from collections import defaultdict
    from statistics import median

    groups = defaultdict(list)

    for post in posts:
        key = (post.content_type, post.hashtag)
        groups[key].append(post)

    recommendations = []

    for (content_type, hashtag), group in groups.items():

        if len(group) < 5:
            continue

        virality_scores = [
            post.virality_score
            for post in group
            if post.virality_score is not None
        ]

        engagement_rates = [
            post.engagement_rate
            for post in group
            if post.engagement_rate is not None
        ]

        avg_shares = (
            sum(post.shares for post in group) / len(group)
        )

        recommendations.append({
            "content_type": content_type,
            "hashtag": hashtag,
            "posts": len(group),
            "median_virality": round(
                median(virality_scores), 2
            ),
            "median_engagement": round(
                median(engagement_rates), 2
            ),
            "avg_shares": round(avg_shares, 2)
        })

    recommendations.sort(
        key=lambda x: (
            x["median_virality"],
            x["median_engagement"]
        ),
        reverse=True
    )

    return recommendations[:10]