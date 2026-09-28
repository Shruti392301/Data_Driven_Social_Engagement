from sqlalchemy import Column, Date, Float, Integer, String, Boolean

from .database import Base


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True)

    post_date = Column(Date)

    platform = Column(String)
    hashtag = Column(String)
    content_type = Column(String)
    region = Column(String)

    views = Column(Integer)
    likes = Column(Integer)
    shares = Column(Integer)
    comments = Column(Integer)

    engagement_level = Column(String)

    engagement_rate = Column(Float)
    share_rate = Column(Float)
    comment_rate = Column(Float)

    viral_coefficient = Column(Float)
    virality_score = Column(Float)

    post_month = Column(Integer)
    post_year = Column(Integer)
    day_of_week = Column(String)

    engagement_anomaly = Column(Boolean)


class SentimentComment(Base):
    __tablename__ = "sentiment_comments"

    id = Column(Integer, primary_key=True, index=True)

    clean_comment = Column(String)
    category = Column(Integer)

    sentiment = Column(String)
    processed_comment = Column(String)
    polarity = Column(Float)
    predicted_sentiment = Column(String)