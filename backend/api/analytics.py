from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.database import get_db
from ..database.models import SocialPost, SentimentComment


router = APIRouter(
    prefix="/api",
    tags=["Analytics"]
)


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    posts = db.query(SocialPost).all()

    if not posts:
        return {
            "total_posts": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_shares": 0,
            "total_comments": 0,
            "median_engagement_rate": 0,
            "median_virality_score": 0,
            "total_comments_analyzed": db.query(SentimentComment).count()
        }

    engagement_rates = [
        post.engagement_rate
        for post in posts
        if post.engagement_rate is not None
    ]

    virality_scores = [
        post.virality_score
        for post in posts
        if post.virality_score is not None
    ]

    from statistics import median

    return {
        "total_posts": len(posts),
        "total_views": sum(post.views for post in posts),
        "total_likes": sum(post.likes for post in posts),
        "total_shares": sum(post.shares for post in posts),
        "total_comments": sum(post.comments for post in posts),
        "median_engagement_rate": round(median(engagement_rates), 2),
        "median_virality_score": round(median(virality_scores), 2),
        "total_comments_analyzed": db.query(SentimentComment).count()
    }


@router.get("/platforms")
def get_platforms(db: Session = Depends(get_db)):
    platforms = (
        db.query(SocialPost.platform)
        .distinct()
        .order_by(SocialPost.platform)
        .all()
    )

    results = []

    from statistics import median

    for (platform,) in platforms:
        posts = (
            db.query(SocialPost)
            .filter(SocialPost.platform == platform)
            .all()
        )

        engagement_rates = [
            post.engagement_rate
            for post in posts
            if post.engagement_rate is not None
        ]

        virality_scores = [
            post.virality_score
            for post in posts
            if post.virality_score is not None
        ]

        results.append({
            "platform": platform,
            "posts": len(posts),
            "avg_views": round(
                sum(post.views for post in posts) / len(posts), 2
            ),
            "avg_likes": round(
                sum(post.likes for post in posts) / len(posts), 2
            ),
            "avg_shares": round(
                sum(post.shares for post in posts) / len(posts), 2
            ),
            "avg_comments": round(
                sum(post.comments for post in posts) / len(posts), 2
            ),
            "median_engagement": round(
                median(engagement_rates), 2
            ),
            "median_virality": round(
                median(virality_scores), 2
            )
        })

    return results

@router.get("/content-types")
def get_content_types(db: Session = Depends(get_db)):
    content_types = (
        db.query(SocialPost.content_type)
        .distinct()
        .order_by(SocialPost.content_type)
        .all()
    )

    results = []

    from statistics import median

    for (content_type,) in content_types:
        posts = (
            db.query(SocialPost)
            .filter(SocialPost.content_type == content_type)
            .all()
        )

        engagement_rates = [
            post.engagement_rate
            for post in posts
            if post.engagement_rate is not None
        ]

        virality_scores = [
            post.virality_score
            for post in posts
            if post.virality_score is not None
        ]

        results.append({
            "content_type": content_type,
            "posts": len(posts),
            "avg_views": round(
                sum(post.views for post in posts) / len(posts), 2
            ),
            "avg_likes": round(
                sum(post.likes for post in posts) / len(posts), 2
            ),
            "avg_shares": round(
                sum(post.shares for post in posts) / len(posts), 2
            ),
            "avg_comments": round(
                sum(post.comments for post in posts) / len(posts), 2
            ),
            "median_engagement": round(
                median(engagement_rates), 2
            ),
            "median_virality": round(
                median(virality_scores), 2
            )
        })

    return results

@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    regions = (
        db.query(SocialPost.region)
        .distinct()
        .order_by(SocialPost.region)
        .all()
    )

    results = []

    from statistics import median

    for (region,) in regions:
        posts = (
            db.query(SocialPost)
            .filter(SocialPost.region == region)
            .all()
        )

        engagement_rates = [
            post.engagement_rate
            for post in posts
            if post.engagement_rate is not None
        ]

        virality_scores = [
            post.virality_score
            for post in posts
            if post.virality_score is not None
        ]

        results.append({
            "region": region,
            "posts": len(posts),
            "avg_views": round(
                sum(post.views for post in posts) / len(posts), 2
            ),
            "avg_likes": round(
                sum(post.likes for post in posts) / len(posts), 2
            ),
            "avg_shares": round(
                sum(post.shares for post in posts) / len(posts), 2
            ),
            "avg_comments": round(
                sum(post.comments for post in posts) / len(posts), 2
            ),
            "median_engagement": round(
                median(engagement_rates), 2
            ),
            "median_virality": round(
                median(virality_scores), 2
            )
        })

    return results

@router.get("/hashtags")
def get_hashtags(db: Session = Depends(get_db)):
    hashtags = (
        db.query(SocialPost.hashtag)
        .distinct()
        .order_by(SocialPost.hashtag)
        .all()
    )

    results = []

    from statistics import median

    for (hashtag,) in hashtags:
        posts = (
            db.query(SocialPost)
            .filter(SocialPost.hashtag == hashtag)
            .all()
        )

        engagement_rates = [
            post.engagement_rate
            for post in posts
            if post.engagement_rate is not None
        ]

        virality_scores = [
            post.virality_score
            for post in posts
            if post.virality_score is not None
        ]

        results.append({
            "hashtag": hashtag,
            "posts": len(posts),
            "avg_views": round(
                sum(post.views for post in posts) / len(posts), 2
            ),
            "avg_likes": round(
                sum(post.likes for post in posts) / len(posts), 2
            ),
            "avg_shares": round(
                sum(post.shares for post in posts) / len(posts), 2
            ),
            "avg_comments": round(
                sum(post.comments for post in posts) / len(posts), 2
            ),
            "median_engagement": round(
                median(engagement_rates), 2
            ),
            "median_virality": round(
                median(virality_scores), 2
            )
        })

    return results

@router.get("/top-posts")
def get_top_posts(
    limit: int = Query(default=10, ge=1, le=100),
    platform: str | None = None,
    content_type: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(SocialPost)

    if platform:
        query = query.filter(SocialPost.platform == platform)

    if content_type:
        query = query.filter(SocialPost.content_type == content_type)

    if region:
        query = query.filter(SocialPost.region == region)

    posts = (
        query
        .order_by(SocialPost.virality_score.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "post_id": post.post_id,
            "date": post.post_date,
            "platform": post.platform,
            "hashtag": post.hashtag,
            "content_type": post.content_type,
            "region": post.region,
            "views": post.views,
            "likes": post.likes,
            "shares": post.shares,
            "comments": post.comments,
            "engagement_rate": round(post.engagement_rate, 2),
            "virality_score": round(post.virality_score, 2)
        }
        for post in posts
    ]

@router.get("/sentiment")
def get_sentiment(db: Session = Depends(get_db)):

    results = (
        db.query(
            SentimentComment.sentiment,
            func.count(SentimentComment.id).label("comments")
        )
        .group_by(SentimentComment.sentiment)
        .all()
    )

    total = sum(row.comments for row in results)

    return [
        {
            "sentiment": row.sentiment,
            "comments": row.comments,
            "percentage": round(
                (row.comments / total) * 100, 2
            ) if total else 0
        }
        for row in results
    ]

