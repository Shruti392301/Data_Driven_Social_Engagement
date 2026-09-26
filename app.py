import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Data-Driven Social Engagement",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Data-Driven Social Engagement Dashboard")
st.caption(
    "Analytics for content performance, virality, audience sentiment and trends"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "outputs", "dashboard")


@st.cache_data
def load_csv(filename):
    path = os.path.join(DASHBOARD_DIR, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    return pd.read_csv(path)


kpi = load_csv("kpi_summary.csv")
platform = load_csv("platform_performance.csv")
content = load_csv("content_performance.csv")
hashtag = load_csv("hashtag_performance.csv")
region = load_csv("region_performance.csv")
monthly = load_csv("monthly_performance.csv")
sentiment = load_csv("sentiment_summary.csv")
viral_posts = load_csv("top_viral_posts.csv")
engaging_posts = load_csv("top_engaging_posts.csv")
forecast = load_csv("future_virality_forecast.csv")


required_files = [
    "kpi_summary.csv",
    "platform_performance.csv",
    "content_performance.csv",
    "hashtag_performance.csv",
    "region_performance.csv",
    "monthly_performance.csv",
    "sentiment_summary.csv",
    "top_viral_posts.csv",
    "top_engaging_posts.csv",
    "future_virality_forecast.csv"
]

missing_files = [
    file for file in required_files
    if not os.path.exists(os.path.join(DASHBOARD_DIR, file))
]

if missing_files:
    st.warning("Some dashboard files are missing:")

    for file in missing_files:
        st.write(f"- {file}")
else:
    st.success("All dashboard data loaded successfully.")

    st.divider()

st.subheader("📌 Key Performance Indicators")

if not kpi.empty:

    metrics = dict(zip(kpi["Metric"], kpi["Value"]))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Posts",
        f"{int(metrics.get('Total Posts', 0)):,}"
    )

    col2.metric(
        "Total Views",
        f"{int(metrics.get('Total Views', 0)):,}"
    )

    col3.metric(
        "Total Likes",
        f"{int(metrics.get('Total Likes', 0)):,}"
    )

    col4.metric(
        "Total Shares",
        f"{int(metrics.get('Total Shares', 0)):,}"
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Total Comments",
        f"{int(metrics.get('Total Comments', 0)):,}"
    )

    col6.metric(
        "Median Engagement",
        f"{metrics.get('Median Engagement Rate', 0):.2f}%"
    )

    col7.metric(
        "Median Virality",
        f"{metrics.get('Median Virality Score', 0):.2f}"
    )

    col8.metric(
        "Comments Analyzed",
        f"{int(metrics.get('Total Comments Analyzed', 0)):,}"
    )
st.divider()

st.subheader("🌐 Platform Performance")

if not platform.empty:

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Median Virality by Platform**")

        platform_virality = platform.set_index("Platform")[
            "Median_Virality"
        ]

        st.bar_chart(platform_virality)

    with col2:
        st.markdown("**Median Engagement by Platform**")

        platform_engagement = platform.set_index("Platform")[
            "Median_Engagement"
        ]

        st.bar_chart(platform_engagement)

    st.dataframe(
        platform,
        use_container_width=True,
        hide_index=True
    )
st.divider()

st.subheader("🎬 Content Type Performance")

if not content.empty:

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Median Virality by Content Type**")

        content_virality = content.set_index("Content_Type")[
            "Median_Virality"
        ]

        st.bar_chart(content_virality)

    with col2:
        st.markdown("**Median Engagement by Content Type**")

        content_engagement = content.set_index("Content_Type")[
            "Median_Engagement"
        ]

        st.bar_chart(content_engagement)

    st.dataframe(
        content,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("📈 Monthly Virality Trend")

if not monthly.empty:

    monthly["Post_Date"] = pd.to_datetime(
        monthly["Post_Date"]
    )

    monthly_chart = monthly.set_index("Post_Date")

    st.line_chart(
        monthly_chart["Median_Virality"]
    )

    st.dataframe(
        monthly,
        use_container_width=True,
        hide_index=True
    )