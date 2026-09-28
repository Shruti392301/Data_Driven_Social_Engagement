from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.database import get_db
from ..database.models import SocialPost

router = APIRouter(prefix="/api", tags=["Forecasting"])


@router.get("/monthly-trends")
def get_monthly_trends(db: Session = Depends(get_db)):

    results = (
        db.query(
            SocialPost.post_year,
            SocialPost.post_month,
            func.count(SocialPost.id).label("post_count"),
            func.sum(SocialPost.views).label("total_views"),
            func.avg(SocialPost.views).label("avg_views"),
            func.avg(SocialPost.likes).label("avg_likes"),
            func.avg(SocialPost.shares).label("avg_shares"),
            func.avg(SocialPost.comments).label("avg_comments")
        )
        .group_by(
            SocialPost.post_year,
            SocialPost.post_month
        )
        .order_by(
            SocialPost.post_year,
            SocialPost.post_month
        )
        .all()
    )

    return [
        {
            "year": row.post_year,
            "month": row.post_month,
            "post_count": row.post_count,
            "total_views": row.total_views,
            "avg_views": round(row.avg_views or 0, 2),
            "avg_likes": round(row.avg_likes or 0, 2),
            "avg_shares": round(row.avg_shares or 0, 2),
            "avg_comments": round(row.avg_comments or 0, 2)
        }
        for row in results
    ]

from statistics import median

from statsmodels.tsa.holtwinters import ExponentialSmoothing


@router.get("/virality-forecast")
def get_virality_forecast(
    months: int = 6,
    db: Session = Depends(get_db)
):
    posts = (
        db.query(SocialPost)
        .order_by(
            SocialPost.post_year,
            SocialPost.post_month
        )
        .all()
    )

    if not posts:
        return {
            "message": "No data available",
            "forecast": []
        }

    monthly_data = {}

    for post in posts:
        key = (post.post_year, post.post_month)

        if key not in monthly_data:
            monthly_data[key] = []

        monthly_data[key].append(post.virality_score)

    dates = []
    values = []

    for (year, month), scores in sorted(monthly_data.items()):
        dates.append(f"{year}-{month:02d}")
        values.append(median(scores))

    if len(values) < 6:
        return {
            "message": "Not enough historical data for forecasting",
            "forecast": []
        }

    model = ExponentialSmoothing(
        values,
        trend="add",
        damped_trend=True,
        initialization_method="estimated"
    )

    fitted_model = model.fit()

    forecast_values = fitted_model.forecast(months)

    forecast = []

    last_year, last_month = sorted(monthly_data.keys())[-1]

    for i, value in enumerate(forecast_values, start=1):

        forecast_month = last_month + i
        forecast_year = last_year

        while forecast_month > 12:
            forecast_month -= 12
            forecast_year += 1

        forecast.append({
            "year": forecast_year,
            "month": forecast_month,
            "predicted_virality": round(float(value), 2)
        })

    return {
        "historical_months": len(values),
        "forecast_months": months,
        "forecast": forecast
    }