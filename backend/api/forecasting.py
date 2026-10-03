from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from ..database.database import get_db
from ..database.models import SocialPost

router = APIRouter(
    prefix="/api",
    tags=["Forecasting"]
)


@router.get("/monthly-trends")
def monthly_trends(db: Session = Depends(get_db)):

    posts = db.query(SocialPost).all()

    if not posts:
        return []

    data = pd.DataFrame([
        {
            "post_date": post.post_date,
            "virality_score": post.virality_score
        }
        for post in posts
    ])

    data["post_date"] = pd.to_datetime(data["post_date"])

    data["month"] = (
        data["post_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        data.groupby("month")
        .agg(
            post_count=("virality_score", "count"),
            median_virality=("virality_score", "median")
        )
        .reset_index()
    )

    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")

    return monthly.to_dict(orient="records")


@router.get("/virality-forecast")
def virality_forecast(
    months: int = Query(
        6,
        ge=1,
        le=12
    ),
    db: Session = Depends(get_db)
):

    posts = db.query(SocialPost).all()

    if not posts:

        return {
            "historical_months": [],
            "historical_virality": [],
            "forecast_months": [],
            "forecast": [],
            "model": "Holt Exponential Smoothing",
            "mae": None,
            "rmse": None
        }

    data = pd.DataFrame([
        {
            "post_date": post.post_date,
            "virality_score": post.virality_score
        }
        for post in posts
    ])

    data["post_date"] = pd.to_datetime(
        data["post_date"]
    )

    data["month"] = (
        data["post_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        data.groupby("month")["virality_score"]
        .median()
        .sort_index()
    )

    monthly = monthly.asfreq("MS")

    monthly = monthly.interpolate(
        method="linear"
    )

    if len(monthly) < 12:

        return {
            "historical_months": [
                x.strftime("%Y-%m")
                for x in monthly.index
            ],
            "historical_virality": [
                round(float(x), 2)
                for x in monthly.values
            ],
            "forecast_months": [],
            "forecast": [],
            "model": "Holt Exponential Smoothing",
            "mae": None,
            "rmse": None,
            "message": "At least 12 months of historical data are required."
        }

    # --------------------------------
    # Train / test split
    # --------------------------------

    train_size = int(
        len(monthly) * 0.8
    )

    train = monthly.iloc[:train_size]

    test = monthly.iloc[train_size:]

    # --------------------------------
    # Validation model
    # --------------------------------

    validation_model = ExponentialSmoothing(
        train,
        trend="add",
        damped_trend=True,
        seasonal=None,
        initialization_method="estimated"
    )

    validation_fit = validation_model.fit(
        optimized=True
    )

    test_prediction = validation_fit.forecast(
        len(test)
    )

    mae = float(
        np.mean(
            np.abs(
                test.values -
                test_prediction.values
            )
        )
    )

    rmse = float(
        np.sqrt(
            np.mean(
                (
                    test.values -
                    test_prediction.values
                ) ** 2
            )
        )
    )

    # --------------------------------
    # Final model
    # --------------------------------

    final_model = ExponentialSmoothing(
        monthly,
        trend="add",
        damped_trend=True,
        seasonal=None,
        initialization_method="estimated"
    )

    final_fit = final_model.fit(
        optimized=True
    )

    future_prediction = final_fit.forecast(
        months
    )

    future_prediction = np.maximum(
        future_prediction,
        0
    )

    # --------------------------------
    # Historical data
    # --------------------------------

    historical_months = [
        x.strftime("%Y-%m")
        for x in monthly.index
    ]

    historical_virality = [
        round(float(x), 2)
        for x in monthly.values
    ]

    # --------------------------------
    # Future data
    # --------------------------------

    forecast_months = [
        x.strftime("%Y-%m")
        for x in future_prediction.index
    ]

    forecast_values = [
        round(float(x), 2)
        for x in future_prediction.values
    ]

    # --------------------------------
    # Response
    # --------------------------------

    return {
        "historical_months": historical_months,
        "historical_virality": historical_virality,
        "forecast_months": forecast_months,
        "forecast": forecast_values,
        "model": "Holt Exponential Smoothing",
        "training_months": len(train),
        "testing_months": len(test),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4)
    }