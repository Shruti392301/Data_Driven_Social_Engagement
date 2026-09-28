from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database.database import Base, engine, get_db
from .database import models
from .services.data_loader import load_all_data
from .api.analytics import router as analytics_router
from .api.forecasting import router as forecasting_router
from .api.recommendations import router as recommendations_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Data-Driven Social Engagement API",
    description="Backend API for social media analytics, sentiment analysis, recommendations and forecasting.",
    version="1.0.0"
)


app.include_router(analytics_router)
app.include_router(forecasting_router)
app.include_router(recommendations_router)

@app.get("/")
def root():
    return {
        "message": "Data-Driven Social Engagement API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/api/load-data")
def load_data(db: Session = Depends(get_db)):
    result = load_all_data(db)

    return {
        "message": "Data loaded successfully",
        "viral_posts": result["viral_posts"],
        "sentiment_comments": result["sentiment_comments"]
    }