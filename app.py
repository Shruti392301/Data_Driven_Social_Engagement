import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Data-Driven Social Engagement",
    page_icon="📊",
    layout="wide"
)


def get_api_data(endpoint, params=None):
    response = requests.get(
        f"{API_URL}{endpoint}",
        params=params,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


st.title("📊 Data-Driven Social Engagement Dashboard")
st.caption(
    "Analytics for content performance, virality, audience sentiment, recommendations and trends"
)


try:
    health = get_api_data("/health")

    if health.get("status") != "healthy":
        st.error("FastAPI backend is not healthy.")
        st.stop()

except Exception as e:
    st.error("❌ Could not connect to FastAPI backend.")
    st.write(str(e))
    st.info(
        "Make sure FastAPI is running with: "
        "`python -m uvicorn backend.main:app --reload`"
    )
    st.stop()


st.success("✅ Connected to FastAPI backend")


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("🎛️ Dashboard Filters")

try:
    platform_data = pd.DataFrame(
        get_api_data("/api/platforms")
    )

    region_data = pd.DataFrame(
        get_api_data("/api/regions")
    )

    content_data = pd.DataFrame(
        get_api_data("/api/content-types")
    )

except Exception as e:
    st.error(f"Could not load filter data: {e}")
    st.stop()


platform_options = ["All"]

if not platform_data.empty:
    platform_options += sorted(
        platform_data["platform"].dropna().unique().tolist()
    )


region_options = ["All"]

if not region_data.empty:
    region_options += sorted(
        region_data["region"].dropna().unique().tolist()
    )


content_options = ["All"]

if not content_data.empty:
    content_options += sorted(
        content_data["content_type"].dropna().unique().tolist()
    )


selected_platform = st.sidebar.selectbox(
    "Platform",
    platform_options
)

selected_region = st.sidebar.selectbox(
    "Region",
    region_options
)

selected_content = st.sidebar.selectbox(
    "Content Type",
    content_options
)


# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------

st.header("📌 Key Performance Indicators")

try:
    summary = get_api_data("/api/summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Posts",
        f"{summary['total_posts']:,}"
    )

    col2.metric(
        "Total Views",
        f"{summary['total_views']:,}"
    )

    col3.metric(
        "Total Likes",
        f"{summary['total_likes']:,}"
    )

    col4.metric(
        "Total Shares",
        f"{summary['total_shares']:,}"
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Total Comments",
        f"{summary['total_comments']:,}"
    )

    col6.metric(
        "Median Engagement",
        f"{summary['median_engagement_rate']:.2f}%"
    )

    col7.metric(
        "Median Virality",
        f"{summary['median_virality_score']:.2f}"
    )

    col8.metric(
        "Comments Analyzed",
        f"{summary['total_comments_analyzed']:,}"
    )

except Exception as e:
    st.error(f"Could not load KPI data: {e}")


st.divider()


# ---------------------------------------------------------
# PLATFORM PERFORMANCE
# ---------------------------------------------------------

st.header("🌐 Platform Performance")

if not platform_data.empty:

    display_platform = platform_data.copy()

    if selected_platform != "All":
        display_platform = display_platform[
            display_platform["platform"] == selected_platform
        ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Median Virality")

        chart_data = display_platform.set_index(
            "platform"
        )["median_virality"]

        st.bar_chart(chart_data)

    with col2:
        st.subheader("Median Engagement")

        chart_data = display_platform.set_index(
            "platform"
        )["median_engagement"]

        st.bar_chart(chart_data)

    st.dataframe(
        display_platform,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ---------------------------------------------------------
# CONTENT TYPE PERFORMANCE
# ---------------------------------------------------------

st.header("🎬 Content Type Performance")

if not content_data.empty:

    display_content = content_data.copy()

    if selected_content != "All":
        display_content = display_content[
            display_content["content_type"] == selected_content
        ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Median Virality")

        chart_data = display_content.set_index(
            "content_type"
        )["median_virality"]

        st.bar_chart(chart_data)

    with col2:
        st.subheader("Median Engagement")

        chart_data = display_content.set_index(
            "content_type"
        )["median_engagement"]

        st.bar_chart(chart_data)

    st.dataframe(
        display_content,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ---------------------------------------------------------
# REGION PERFORMANCE
# ---------------------------------------------------------

st.header("🌍 Region Performance")

if not region_data.empty:

    display_region = region_data.copy()

    if selected_region != "All":
        display_region = display_region[
            display_region["region"] == selected_region
        ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Median Virality by Region")

        chart_data = display_region.set_index(
            "region"
        )["median_virality"]

        st.bar_chart(chart_data)

    with col2:
        st.subheader("Median Engagement by Region")

        chart_data = display_region.set_index(
            "region"
        )["median_engagement"]

        st.bar_chart(chart_data)

    st.dataframe(
        display_region,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ---------------------------------------------------------
# HASHTAG PERFORMANCE
# ---------------------------------------------------------

st.header("#️⃣ Hashtag Performance")

try:
    hashtag_data = pd.DataFrame(
        get_api_data("/api/hashtags")
    )

    if not hashtag_data.empty:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Median Virality by Hashtag")

            chart_data = hashtag_data.set_index(
                "hashtag"
            )["median_virality"]

            st.bar_chart(chart_data)

        with col2:
            st.subheader("Median Engagement by Hashtag")

            chart_data = hashtag_data.set_index(
                "hashtag"
            )["median_engagement"]

            st.bar_chart(chart_data)

        st.dataframe(
            hashtag_data,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Could not load hashtag data: {e}")


st.divider()


# ---------------------------------------------------------
# MONTHLY TRENDS
# ---------------------------------------------------------

st.header("📈 Monthly Trends")

try:
    monthly_data = pd.DataFrame(
        get_api_data("/api/monthly-trends")
    )

    if not monthly_data.empty:

        monthly_data["Date"] = pd.to_datetime(
            monthly_data["year"].astype(str)
            + "-"
            + monthly_data["month"].astype(str)
            + "-01"
        )

        monthly_data = monthly_data.set_index("Date")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Average Views")

            st.line_chart(
                monthly_data["avg_views"]
            )

        with col2:
            st.subheader("Total Views")

            st.line_chart(
                monthly_data["total_views"]
            )

        st.dataframe(
            monthly_data.reset_index(),
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Could not load monthly trends: {e}")


st.divider()


# ---------------------------------------------------------
# SENTIMENT ANALYSIS
# ---------------------------------------------------------

st.header("💬 Audience Sentiment")

try:
    sentiment_data = pd.DataFrame(
        get_api_data("/api/sentiment")
    )

    if not sentiment_data.empty:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sentiment Distribution")

            chart_data = sentiment_data.set_index(
                "sentiment"
            )["count"]

            st.bar_chart(chart_data)

        with col2:
            st.subheader("Sentiment Percentage")

            chart_data = sentiment_data.set_index(
                "sentiment"
            )["percentage"]

            st.bar_chart(chart_data)

        st.dataframe(
            sentiment_data,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Could not load sentiment data: {e}")


st.divider()


# ---------------------------------------------------------
# TOP VIRAL POSTS
# ---------------------------------------------------------

st.header("🔥 Top Viral Posts")

try:
    post_params = {
        "limit": 10
    }

    if selected_platform != "All":
        post_params["platform"] = selected_platform

    if selected_region != "All":
        post_params["region"] = selected_region

    if selected_content != "All":
        post_params["content_type"] = selected_content

    viral_posts = pd.DataFrame(
        get_api_data(
            "/api/top-posts",
            params=post_params
        )
    )

    if not viral_posts.empty:

        st.dataframe(
            viral_posts,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No posts found for the selected filters."
        )

except Exception as e:
    st.error(f"Could not load top viral posts: {e}")


st.divider()


# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------

st.header("💡 Content Recommendations")

try:
    recommendation_params = {}

    if selected_platform != "All":
        recommendation_params["platform"] = selected_platform

    if selected_region != "All":
        recommendation_params["region"] = selected_region

    recommendations = pd.DataFrame(
        get_api_data(
            "/api/recommendations",
            params=recommendation_params
        )
    )

    if not recommendations.empty:

        st.dataframe(
            recommendations,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No recommendations available for the selected filters."
        )

except Exception as e:
    st.error(
        f"Could not load recommendations: {e}"
    )


st.divider()


# ---------------------------------------------------------
# VIRALITY FORECAST
# ---------------------------------------------------------

st.header("🔮 Virality Forecast")

try:
    forecast_response = get_api_data(
        "/api/virality-forecast"
    )

    forecast_data = pd.DataFrame(
        forecast_response["forecast"]
    )

    if not forecast_data.empty:

        forecast_data["Date"] = pd.to_datetime(
            forecast_data["year"].astype(str)
            + "-"
            + forecast_data["month"].astype(str)
            + "-01"
        )

        forecast_data = forecast_data.set_index(
            "Date"
        )

        st.line_chart(
            forecast_data["predicted_virality"]
        )

        st.dataframe(
            forecast_data.reset_index(),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No forecast data available."
        )

except Exception as e:
    st.error(
        f"Could not load forecast data: {e}"
    )


st.divider()


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.caption(
    "Data-Driven Social Engagement Dashboard | "
    "FastAPI + SQLite + SQLAlchemy + Streamlit"
)