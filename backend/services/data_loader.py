from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from ..database.models import SocialPost, SentimentComment


BASE_DIR = Path(__file__).resolve().parents[2]

VIRAL_FILE = BASE_DIR / "data" / "raw" / "Cleaned_Viral_Social_Media_Trends.csv"
SENTIMENT_FILE = BASE_DIR / "data" / "raw" / "Social media_Data.csv"


def load_viral_data(db: Session):
    df = pd.read_csv(VIRAL_FILE)

    df["Post_Date"] = pd.to_datetime(df["Post_Date"])

    df["Engagement_Rate"] = (
        (df["Likes"] + df["Shares"] + df["Comments"])
        / df["Views"]
    ) * 100

    df["Share_Rate"] = (
        df["Shares"] / df["Views"]
    ) * 100

    df["Comment_Rate"] = (
        df["Comments"] / df["Views"]
    ) * 100

    df["Viral_Coefficient"] = (
        0.60 * (df["Shares"] / df["Views"])
        + 0.20 * (df["Comments"] / df["Views"])
        + 0.20 * (df["Likes"] / df["Views"])
    )

    df["Virality_Score"] = df["Viral_Coefficient"] * 100

    df["Post_Month"] = df["Post_Date"].dt.month
    df["Post_Year"] = df["Post_Date"].dt.year
    df["Day_of_Week"] = df["Post_Date"].dt.day_name()

    df["Engagement_Anomaly"] = (
        (df["Likes"] > df["Views"])
        | (df["Shares"] > df["Views"])
        | (df["Comments"] > df["Views"])
    )

    db.query(SocialPost).delete()

    records = []

    for _, row in df.iterrows():
        records.append(
            SocialPost(
                post_id=row["Post_ID"],
                post_date=row["Post_Date"].date(),
                platform=row["Platform"],
                hashtag=row["Hashtag"],
                content_type=row["Content_Type"],
                region=row["Region"],
                views=int(row["Views"]),
                likes=int(row["Likes"]),
                shares=int(row["Shares"]),
                comments=int(row["Comments"]),
                engagement_level=row["Engagement_Level"],
                engagement_rate=float(row["Engagement_Rate"]),
                share_rate=float(row["Share_Rate"]),
                comment_rate=float(row["Comment_Rate"]),
                viral_coefficient=float(row["Viral_Coefficient"]),
                virality_score=float(row["Virality_Score"]),
                post_month=int(row["Post_Month"]),
                post_year=int(row["Post_Year"]),
                day_of_week=row["Day_of_Week"],
                engagement_anomaly=bool(row["Engagement_Anomaly"])
            )
        )

    db.bulk_save_objects(records)
    db.commit()

    return len(records)


def load_sentiment_data(db: Session):
    df = pd.read_csv(SENTIMENT_FILE)

    df = df.dropna(subset=["clean_comment"])

    df = df.drop_duplicates(
        subset=["clean_comment"],
        keep="first"
    )

    df["clean_comment"] = (
        df["clean_comment"]
        .astype(str)
        .str.strip()
    )

    df = df[df["clean_comment"] != ""].copy()

    df["Sentiment"] = df["category"].map({
        1: "Positive",
        0: "Neutral",
        -1: "Negative"
    })

    db.query(SentimentComment).delete()

    records = []

    for _, row in df.iterrows():
        records.append(
            SentimentComment(
                clean_comment=row["clean_comment"],
                category=int(row["category"]),
                sentiment=row["Sentiment"]
            )
        )

    db.bulk_save_objects(records)
    db.commit()

    return len(records)


def load_all_data(db: Session):
    viral_count = load_viral_data(db)
    sentiment_count = load_sentiment_data(db)

    return {
        "viral_posts": viral_count,
        "sentiment_comments": sentiment_count
    }