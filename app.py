import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="SocialPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# API FUNCTIONS
# ============================================================

def get_api_data(endpoint, params=None):
    response = requests.get(
        f"{API_URL}{endpoint}",
        params=params,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def backend_available():
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


# ============================================================
# NAVIGATION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"


def go_to(page):
    st.session_state.page = page
    st.rerun()


# ============================================================
# BACKEND CHECK
# ============================================================

if not backend_available():

    st.error("❌ SocialPulse backend is not running.")

    st.info(
        "Start FastAPI using:\n\n"
        "`python -m uvicorn backend.main:app --reload`"
    )

    st.stop()


# ============================================================
# HOME PAGE
# ============================================================
if st.session_state.page == "Home":

    st.markdown(
        """
        <div style="text-align: center; padding: 35px 0 20px 0;">
            <h1 style="font-size: 52px;">📊 SocialPulse</h1>
            <h3>A Data-Driven Social Media Engagement Intelligence System</h3>
            <p style="font-size: 18px;">
                Understand content performance, virality, audience sentiment
                and social media trends through data.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "<h2 style='text-align:center;'>What would you like to explore?</h2>",
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Explore Analytics")
        st.write(
            "Explore platform, region, content type and hashtag performance."
        )

        if st.button(
            "Explore Analytics →",
            key="analytics_button",
            use_container_width=True
        ):
            go_to("Explore Analytics")

    with col2:
        st.markdown("### 🚀 Virality Explorer")
        st.write(
            "Explore viral posts and calculate the virality of custom content."
        )

        if st.button(
            "Explore Virality →",
            key="virality_button",
            use_container_width=True
        ):
            go_to("Virality")

    st.write("")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 💬 Audience Insights")
        st.write(
            "Understand positive, neutral and negative audience sentiment."
        )

        if st.button(
            "Explore Audience →",
            key="audience_button",
            use_container_width=True
        ):
            go_to("Audience")

    with col4:
        st.markdown("### 🎯 Recommendations")
        st.write(
            "Get content and hashtag recommendations based on historical data."
        )

        if st.button(
            "Get Recommendations →",
            key="recommendation_button",
            use_container_width=True
        ):
            go_to("Recommendations")

    st.write("")

    col5, col6 = st.columns(2)

    with col5:
        st.markdown("### 📈 Forecast")
        st.write(
            "Explore estimated future virality based on historical trends."
        )

        if st.button(
            "View Forecast →",
            key="forecast_button",
            use_container_width=True
        ):
            go_to("Forecast")

    with col6:
        st.markdown("### 🔗 Post Analyzer")
        st.write(
            "Analyze an individual social media post and compare its "
            "performance with SocialPulse historical data."
        )

        if st.button(
            "Analyze a Post →",
            key="post_analyzer_button",
            use_container_width=True
        ):
            go_to("Post Analyzer")


# ============================================================
# EXPLORE ANALYTICS
# ============================================================

elif st.session_state.page == "Explore Analytics":

    if st.button("← Back to Home"):
        go_to("Home")

    st.title("📊 Explore Analytics")

    st.write(
        "Explore how social media performance varies across platforms, "
        "regions, content types and hashtags."
    )

    st.divider()

    st.markdown("## 📌 Overall Performance")

    summary = get_api_data("/api/summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Posts",
            f"{summary['total_posts']:,}"
        )

    with col2:
        st.metric(
            "Total Views",
            f"{summary['total_views']:,}"
        )

    with col3:
        st.metric(
            "Total Likes",
            f"{summary['total_likes']:,}"
        )

    with col4:
        st.metric(
            "Total Shares",
            f"{summary['total_shares']:,}"
        )

    st.divider()

    st.markdown("## 📈 Performance Explorer")

    metric = st.selectbox(
        "Choose a metric to explore",
        [
            "Median Engagement",
            "Median Virality"
        ],
        key="analytics_metric"
    )

    st.caption(
        "Use this selector to compare different dimensions of social media performance."
    )

    # Platform
    st.markdown("### 📱 Platform Performance")

    platform_data = pd.DataFrame(
        get_api_data("/api/platforms")
    )

    if metric == "Median Engagement":

        fig_platform = px.bar(
            platform_data,
            x="platform",
            y="median_engagement",
            title="Engagement by Platform",
            labels={
                "platform": "Platform",
                "median_engagement": "Median Engagement (%)"
            },
            text_auto=".2f"
        )

    else:

        fig_platform = px.bar(
            platform_data,
            x="platform",
            y="median_virality",
            title="Virality by Platform",
            labels={
                "platform": "Platform",
                "median_virality": "Median Virality Score"
            },
            text_auto=".2f"
        )

    st.plotly_chart(
        fig_platform,
        use_container_width=True
    )

    st.info(
        "This chart compares historical social media performance across "
        "Instagram, TikTok, Twitter and YouTube."
    )

    # Region
    st.markdown("### 🌍 Regional Performance")

    region_data = pd.DataFrame(
        get_api_data("/api/regions")
    )

    if metric == "Median Engagement":

        region_data = region_data.sort_values(
            "median_engagement",
            ascending=False
        )

        fig_region = px.bar(
            region_data,
            x="region",
            y="median_engagement",
            title="Engagement by Region",
            labels={
                "region": "Region",
                "median_engagement": "Median Engagement (%)"
            },
            text_auto=".2f"
        )

    else:

        region_data = region_data.sort_values(
            "median_virality",
            ascending=False
        )

        fig_region = px.bar(
            region_data,
            x="region",
            y="median_virality",
            title="Virality by Region",
            labels={
                "region": "Region",
                "median_virality": "Median Virality Score"
            },
            text_auto=".2f"
        )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

    st.info(
        "Regional analysis shows how historical social media performance "
        "varies across different geographic regions."
    )

    # Content type
    st.markdown("### 🎬 Content Type Performance")

    content_data = pd.DataFrame(
        get_api_data("/api/content-types")
    )

    if metric == "Median Engagement":

        content_data = content_data.sort_values(
            "median_engagement",
            ascending=False
        )

        fig_content = px.bar(
            content_data,
            x="content_type",
            y="median_engagement",
            title="Engagement by Content Type",
            labels={
                "content_type": "Content Type",
                "median_engagement": "Median Engagement (%)"
            },
            text_auto=".2f"
        )

    else:

        content_data = content_data.sort_values(
            "median_virality",
            ascending=False
        )

        fig_content = px.bar(
            content_data,
            x="content_type",
            y="median_virality",
            title="Virality by Content Type",
            labels={
                "content_type": "Content Type",
                "median_virality": "Median Virality Score"
            },
            text_auto=".2f"
        )

    st.plotly_chart(
        fig_content,
        use_container_width=True
    )

    st.info(
        "This comparison shows how different content formats are associated "
        "with engagement and virality in the dataset."
    )

    # Hashtags
    st.markdown("### #️⃣ Hashtag Performance")

    hashtag_data = pd.DataFrame(
        get_api_data("/api/hashtags")
    )

    if metric == "Median Engagement":

        hashtag_data = hashtag_data.sort_values(
            "median_engagement",
            ascending=True
        )

        fig_hashtag = px.bar(
            hashtag_data,
            x="median_engagement",
            y="hashtag",
            orientation="h",
            title="Engagement by Hashtag",
            labels={
                "hashtag": "Hashtag",
                "median_engagement": "Median Engagement (%)"
            },
            text_auto=".2f"
        )

    else:

        hashtag_data = hashtag_data.sort_values(
            "median_virality",
            ascending=True
        )

        fig_hashtag = px.bar(
            hashtag_data,
            x="median_virality",
            y="hashtag",
            orientation="h",
            title="Virality by Hashtag",
            labels={
                "hashtag": "Hashtag",
                "median_virality": "Median Virality Score"
            },
            text_auto=".2f"
        )

    st.plotly_chart(
        fig_hashtag,
        use_container_width=True
    )

    st.info(
        "Hashtag analysis shows the historical engagement or virality "
        "associated with different hashtags."
    )


# ============================================================
# VIRALITY EXPLORER
# ============================================================

elif st.session_state.page == "Virality":

    if st.button("← Back to Home"):
        go_to("Home")

    st.title("🚀 Virality Explorer")

    st.write(
        "Explore highly viral posts and calculate a virality score "
        "for custom engagement data."
    )

    st.divider()

    # --------------------------------------------------------
    # TOP VIRAL POSTS
    # --------------------------------------------------------

    st.markdown("## 🔥 Top Viral Posts")

    col1, col2, col3 = st.columns(3)

    with col1:

        platform_filter = st.selectbox(
            "Platform",
            [
                "All",
                "Instagram",
                "TikTok",
                "Twitter",
                "YouTube"
            ],
            key="viral_platform"
        )

    with col2:

        content_filter = st.selectbox(
            "Content Type",
            [
                "All",
                "Video",
                "Shorts",
                "Post",
                "Tweet",
                "Live Stream",
                "Reel"
            ],
            key="viral_content"
        )

    with col3:

        region_filter = st.selectbox(
            "Region",
            [
                "All",
                "India",
                "USA",
                "UK",
                "Canada",
                "Brazil",
                "Australia",
                "Japan",
                "Germany"
            ],
            key="viral_region"
        )

    params = {
        "limit": 10
    }

    if platform_filter != "All":
        params["platform"] = platform_filter

    if content_filter != "All":
        params["content_type"] = content_filter

    if region_filter != "All":
        params["region"] = region_filter

    top_posts = pd.DataFrame(
        get_api_data(
            "/api/top-posts",
            params=params
        )
    )

    if not top_posts.empty:

        st.dataframe(
            top_posts,
            use_container_width=True,
            hide_index=True
        )

        if "virality_score" in top_posts.columns:

            fig_top = px.bar(
                top_posts.sort_values(
                    "virality_score",
                    ascending=True
                ),
                x="virality_score",
                y="post_id",
                orientation="h",
                title="Top Viral Posts",
                labels={
                    "virality_score": "Virality Score",
                    "post_id": "Post"
                },
                text_auto=".2f"
            )

            st.plotly_chart(
                fig_top,
                use_container_width=True
            )

    else:

        st.warning(
            "No posts found for the selected filters."
        )

    st.divider()

    # --------------------------------------------------------
    # VIRALITY CALCULATOR
    # --------------------------------------------------------

    st.markdown("## 🧮 Virality Calculator")

    st.write(
        "Enter engagement values to calculate the SocialPulse "
        "virality score."
    )

    col1, col2 = st.columns(2)

    with col1:

        views = st.number_input(
            "Views",
            min_value=1,
            value=100000,
            step=1000,
            key="calc_views"
        )

        likes = st.number_input(
            "Likes",
            min_value=0,
            value=10000,
            step=100,
            key="calc_likes"
        )

    with col2:

        shares = st.number_input(
            "Shares",
            min_value=0,
            value=5000,
            step=100,
            key="calc_shares"
        )

        comments = st.number_input(
            "Comments",
            min_value=0,
            value=1000,
            step=100,
            key="calc_comments"
        )

    if st.button(
        "Calculate Virality",
        use_container_width=True
    ):

        viral_coefficient = (
            0.60 * (shares / views)
            + 0.20 * (comments / views)
            + 0.20 * (likes / views)
        )

        virality_score = viral_coefficient * 100

        engagement_rate = (
            (likes + shares + comments)
            / views
        ) * 100

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Engagement Rate",
                f"{engagement_rate:.2f}%"
            )

        with col2:

            st.metric(
                "Virality Coefficient",
                f"{viral_coefficient:.4f}"
            )

        with col3:

            st.metric(
                "Virality Score",
                f"{virality_score:.2f}"
            )

        st.info(
            "SocialPulse calculates virality using weighted shares, "
            "comments and likes relative to views. Shares have the "
            "highest weight in the current project formula."
        )


# ============================================================
# AUDIENCE INSIGHTS
# ============================================================
elif st.session_state.page == "Audience":

    if st.button("← Back to Home"):
        go_to("Home")

    st.title("💬 Audience Insights")

    st.write(
        "Understand the distribution of positive, neutral and negative "
        "audience sentiment in the analyzed comments."
    )

    st.divider()

    sentiment_data = pd.DataFrame(
        get_api_data("/api/sentiment")
    )

    # --------------------------------------------------------
    # CHECK API DATA
    # --------------------------------------------------------

    if sentiment_data.empty:

        st.warning("No sentiment data is available.")

    else:

        # Detect the actual count column returned by the API
        possible_count_columns = [
            "count",
            "comments",
            "total",
            "value",
            "frequency"
        ]

        count_column = None

        for column in possible_count_columns:
            if column in sentiment_data.columns:
                count_column = column
                break

        # Detect sentiment column
        if "sentiment" in sentiment_data.columns:
            sentiment_column = "sentiment"

        elif "category" in sentiment_data.columns:
            sentiment_column = "category"

        else:
            sentiment_column = sentiment_data.columns[0]

        # ----------------------------------------------------
        # IF COUNT COLUMN EXISTS
        # ----------------------------------------------------

        if count_column is not None:

            sentiment_data["count_value"] = pd.to_numeric(
                sentiment_data[count_column],
                errors="coerce"
            )

            total_comments = sentiment_data["count_value"].sum()

            sentiment_data["percentage"] = (
                sentiment_data["count_value"]
                / total_comments
            ) * 100

        # ----------------------------------------------------
        # IF API ALREADY RETURNS PERCENTAGE
        # ----------------------------------------------------

        elif "percentage" in sentiment_data.columns:

            sentiment_data["percentage"] = pd.to_numeric(
                sentiment_data["percentage"],
                errors="coerce"
            )

            total_comments = None

        else:

            st.error(
                "The sentiment API response does not contain a usable "
                "count or percentage column."
            )

            st.write("API columns returned:")

            st.write(
                list(sentiment_data.columns)
            )

            st.stop()

        # ----------------------------------------------------
        # SENTIMENT SUMMARY
        # ----------------------------------------------------

        st.markdown("## 📌 Sentiment Summary")

        col1, col2, col3, col4 = st.columns(4)

        # Total comments
        with col1:

            if total_comments is not None:

                st.metric(
                    "Comments Analyzed",
                    f"{int(total_comments):,}"
                )

            else:

                st.metric(
                    "Sentiment Categories",
                    len(sentiment_data)
                )

        # Positive
        positive_rows = sentiment_data[
            sentiment_data[sentiment_column]
            .astype(str)
            .str.lower()
            .eq("positive")
        ]

        positive_value = (
            positive_rows["percentage"].iloc[0]
            if not positive_rows.empty
            else 0
        )

        with col2:

            st.metric(
                "Positive",
                f"{positive_value:.2f}%"
            )

        # Neutral
        neutral_rows = sentiment_data[
            sentiment_data[sentiment_column]
            .astype(str)
            .str.lower()
            .eq("neutral")
        ]

        neutral_value = (
            neutral_rows["percentage"].iloc[0]
            if not neutral_rows.empty
            else 0
        )

        with col3:

            st.metric(
                "Neutral",
                f"{neutral_value:.2f}%"
            )

        # Negative
        negative_rows = sentiment_data[
            sentiment_data[sentiment_column]
            .astype(str)
            .str.lower()
            .eq("negative")
        ]

        negative_value = (
            negative_rows["percentage"].iloc[0]
            if not negative_rows.empty
            else 0
        )

        with col4:

            st.metric(
                "Negative",
                f"{negative_value:.2f}%"
            )

        st.divider()

        # ----------------------------------------------------
        # SENTIMENT VISUALIZATION
        # ----------------------------------------------------

        st.markdown("## 📊 Audience Sentiment Distribution")

        chart_data = sentiment_data.copy()

        chart_data["sentiment_display"] = (
            chart_data[sentiment_column]
            .astype(str)
        )

        col1, col2 = st.columns(2)

        # Bar chart
        with col1:

            fig_sentiment_bar = px.bar(
                chart_data,
                x="sentiment_display",
                y="percentage",
                title="Sentiment Distribution",
                labels={
                    "sentiment_display": "Sentiment",
                    "percentage": "Percentage (%)"
                },
                text_auto=".2f"
            )

            fig_sentiment_bar.update_layout(
                xaxis_title=None,
                yaxis_title="Percentage (%)"
            )

            st.plotly_chart(
                fig_sentiment_bar,
                use_container_width=True
            )

        # Pie chart
        with col2:

            if "count_value" in chart_data.columns:

                fig_sentiment_pie = px.pie(
                    chart_data,
                    names="sentiment_display",
                    values="count_value",
                    title="Audience Sentiment",
                    hole=0.45
                )

                st.plotly_chart(
                    fig_sentiment_pie,
                    use_container_width=True
                )

            else:

                fig_sentiment_pie = px.pie(
                    chart_data,
                    names="sentiment_display",
                    values="percentage",
                    title="Audience Sentiment",
                    hole=0.45
                )

                st.plotly_chart(
                    fig_sentiment_pie,
                    use_container_width=True
                )

        st.info(
            "Sentiment analysis provides an overall view of audience "
            "reaction within the analyzed comment dataset."
        )

        st.divider()

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        st.markdown("## 📋 Sentiment Details")

        st.dataframe(
            sentiment_data,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# RECOMMENDATIONS
# ============================================================

elif st.session_state.page == "Recommendations":

    if st.button("← Back to Home"):
        go_to("Home")

    st.title("🎯 Content Recommendations")

    st.write(
        "Discover content type and hashtag combinations that have "
        "performed well historically."
    )

    st.divider()

    # ========================================================
    # TARGET SELECTION
    # ========================================================

    st.markdown("## 🔎 Choose Your Target")

    col1, col2 = st.columns(2)

    with col1:

        recommendation_platform = st.selectbox(
            "Select Platform",
            [
                "All",
                "Instagram",
                "TikTok",
                "Twitter",
                "YouTube"
            ],
            key="recommend_platform"
        )

    with col2:

        recommendation_region = st.selectbox(
            "Select Region",
            [
                "All",
                "India",
                "USA",
                "UK",
                "Canada",
                "Brazil",
                "Australia",
                "Japan",
                "Germany"
            ],
            key="recommend_region"
        )

    # ========================================================
    # API PARAMETERS
    # ========================================================

    params = {}

    if recommendation_platform != "All":
        params["platform"] = recommendation_platform

    if recommendation_region != "All":
        params["region"] = recommendation_region

    # ========================================================
    # GET RECOMMENDATIONS
    # ========================================================

    recommendations_response = get_api_data(
        "/api/recommendations",
        params=params
    )

    recommendations = pd.DataFrame(
        recommendations_response
    )

    st.divider()

    # ========================================================
    # DISPLAY RECOMMENDATIONS
    # ========================================================

    st.markdown("## 💡 Recommended Content Patterns")

    if recommendations.empty:

        st.warning(
            "No recommendations found for the selected filters."
        )

    else:

        # ====================================================
        # SUMMARY METRICS
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Recommendations",
                len(recommendations)
            )

        with col2:

            st.metric(
                "Top Virality",
                f"{recommendations['median_virality'].max():.2f}"
            )

        with col3:

            st.metric(
                "Top Engagement",
                f"{recommendations['median_engagement'].max():.2f}%"
            )

        st.write("")

        # ====================================================
        # CREATE CONTENT PATTERN
        # ====================================================

        recommendations["pattern"] = (
            recommendations["content_type"]
            + " + "
            + recommendations["hashtag"]
        )

        chart_data = recommendations.head(10).copy()

        chart_data = chart_data.sort_values(
            "median_virality",
            ascending=True
        )

        # ====================================================
        # RECOMMENDATION CHART
        # ====================================================

        fig_recommendation = px.bar(
            chart_data,
            x="median_virality",
            y="pattern",
            orientation="h",
            title="Historical Virality of Recommended Content Patterns",
            labels={
                "median_virality": "Median Virality Score",
                "pattern": "Content Pattern"
            },
            text_auto=".2f"
        )

        fig_recommendation.update_layout(
            xaxis_title="Median Virality Score",
            yaxis_title=None
        )

        st.plotly_chart(
            fig_recommendation,
            use_container_width=True
        )

        st.info(
            "Recommendations are based on historical performance "
            "in the SocialPulse dataset. They represent observed "
            "content patterns and are not guaranteed future outcomes."
        )

        st.divider()

        # ====================================================
        # RECOMMENDATION TABLE
        # ====================================================

        st.markdown("## 📋 Recommendation Details")

        display_columns = [
            "content_type",
            "hashtag",
            "posts",
            "median_virality",
            "median_engagement",
            "avg_shares"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in recommendations.columns
        ]

        st.dataframe(
            recommendations[available_columns],
            use_container_width=True,
            hide_index=True
        )
# ============================================================
# FORECAST
# ============================================================
elif st.session_state.page == "Forecast":

    st.markdown(
        """
        <div style="text-align:center; padding:25px 0 15px 0;">
            <h1>📈 Future Virality Forecast</h1>
            <p>
                Predict future social media virality using historical
                monthly engagement patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 🔮 Forecast Settings")

    forecast_months = st.selectbox(
        "Forecast future virality for:",
        [3, 6, 9, 12],
        index=1,
        format_func=lambda x: f"Next {x} months",
        key="forecast_period"
    )

    try:

        response = get_api_data(
            "/api/virality-forecast",
            params={
                "months": forecast_months
            }
        )

        historical_months = response[
            "historical_months"
        ]

        historical_values = response[
            "historical_virality"
        ]

        future_months = response[
            "forecast_months"
        ]

        future_values = response[
            "forecast"
        ]

        model_name = response.get(
            "model",
            "Holt Exponential Smoothing"
        )

        mae = response.get("mae")
        rmse = response.get("rmse")

        # --------------------------------
        # Create historical dataframe
        # --------------------------------

        historical_df = pd.DataFrame({
            "Month": pd.to_datetime(
                historical_months
            ),
            "Virality": historical_values,
            "Type": "Historical"
        })

        # --------------------------------
        # Create forecast dataframe
        # --------------------------------

        forecast_df = pd.DataFrame({
            "Month": pd.to_datetime(
                future_months
            ),
            "Virality": future_values,
            "Type": "Forecast"
        })

        # --------------------------------
        # Combined chart
        # --------------------------------

        combined_df = pd.concat(
            [
                historical_df,
                forecast_df
            ],
            ignore_index=True
        )

        st.markdown(
            "### 📊 Historical vs Future Virality"
        )

        fig = px.line(
            combined_df,
            x="Month",
            y="Virality",
            color="Type",
            markers=True,
            title="Social Media Virality Trend and Forecast"
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Virality Score",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # --------------------------------
        # Forecast summary
        # --------------------------------

        st.markdown("### 📌 Forecast Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Forecast Period",
                f"{forecast_months} Months"
            )

        with col2:

            st.metric(
                "Starting Forecast",
                f"{float(future_values[0]):.2f}"
            )

        with col3:

            st.metric(
                "Final Forecast",
                f"{float(future_values[-1]):.2f}"
            )

        with col4:

            change = (
                float(future_values[-1])
                -
                float(future_values[0])
            )

            st.metric(
                "Forecast Change",
                f"{change:+.2f}"
            )

        # --------------------------------
        # Model
        # --------------------------------

        st.divider()

        st.markdown(
            "### 🤖 Forecasting Model"
        )

        st.info(
            f"""
            **Model:** {model_name}

            The model learns the historical monthly virality
            pattern and estimates future virality values.
            """
        )

        # --------------------------------
        # Evaluation
        # --------------------------------

        if mae is not None and rmse is not None:

            st.markdown(
                "### 📏 Model Evaluation"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "MAE",
                    f"{float(mae):.4f}"
                )

            with col2:

                st.metric(
                    "RMSE",
                    f"{float(rmse):.4f}"
                )

        # --------------------------------
        # Forecast table
        # --------------------------------

        st.markdown(
            "### 📋 Future Forecast Details"
        )

        display_df = forecast_df.copy()

        display_df["Month"] = (
            display_df["Month"]
            .dt.strftime("%B %Y")
        )

        display_df["Virality"] = (
            display_df["Virality"]
            .round(2)
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:

        st.error(
            f"Unable to generate forecast: {e}"
        )
# ============================================================
# POST ANALYZER
# ============================================================

elif st.session_state.page == "Post Analyzer":

    if st.button("← Back to Home"):
        go_to("Home")

    st.markdown(
        """
        <div style="text-align:center; padding:25px 0 15px 0;">
            <h1>🔗 Social Media Post Analyzer</h1>
            <p>
                Automatically analyze a social media post using
                its URL and available platform metrics.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ========================================================
    # URL INPUT
    # ========================================================

    st.markdown("## 🔗 Enter Social Media Post")

    st.write(
        "Paste the URL of a social media post. "
        "SocialPulse will automatically detect the platform, "
        "extract the post ID and retrieve the available metrics."
    )

    post_url = st.text_input(
        "Social Media Post URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="post_analyzer_url"
    )

    st.caption(
        "Currently configured for automatic metric extraction "
        "through supported platform APIs."
    )

    st.write("")

    analyze_button = st.button(
        "🔍 Analyze Post",
        type="primary",
        use_container_width=True
    )

    # ========================================================
    # ANALYSIS
    # ========================================================

    if analyze_button:

        if not post_url.strip():

            st.warning(
                "Please paste a social media post URL."
            )

        else:

            try:

                with st.spinner(
                    "Extracting post metrics..."
                ):

                    response = requests.post(
                        f"{API_URL}/api/analyze-post",
                        json={
                            "url": post_url.strip()
                        },
                        timeout=30
                    )

                # ------------------------------------------------
                # API ERROR
                # ------------------------------------------------

                if response.status_code != 200:

                    try:

                        error_data = response.json()

                        error_message = error_data.get(
                            "detail",
                            "Unable to analyze this post."
                        )

                    except Exception:

                        error_message = (
                            "Unable to analyze this post."
                        )

                    st.error(
                        f"❌ {error_message}"
                    )

                else:

                    result = response.json()

                    st.success(
                        "✅ Post analyzed successfully."
                    )

                    # ====================================================
                    # POST INFORMATION
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 📌 Post Information"
                    )

                    post_info = result["post"]

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Platform",
                            post_info["platform"]
                        )

                    with col2:

                        st.metric(
                            "Post ID",
                            post_info["post_id"]
                        )

                    with col3:

                        if post_info.get("title"):

                            st.metric(
                                "Post",
                                "Detected"
                            )

                        else:

                            st.metric(
                                "Post",
                                "Detected"
                            )

                    if post_info.get("title"):

                        st.write(
                            f"**Title:** {post_info['title']}"
                        )

                    if post_info.get("published_at"):

                        st.write(
                            f"**Published:** "
                            f"{post_info['published_at']}"
                        )

                    # ====================================================
                    # AUTOMATICALLY EXTRACTED METRICS
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 📊 Automatically Extracted Metrics"
                    )

                    raw = result["raw_metrics"]

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Views",
                            f"{raw['views']:,}"
                        )

                    with col2:

                        st.metric(
                            "Likes",
                            f"{raw['likes']:,}"
                        )

                    with col3:

                        st.metric(
                            "Shares",
                            f"{raw['shares']:,}"
                        )

                    with col4:

                        st.metric(
                            "Comments",
                            f"{raw['comments']:,}"
                        )

                    st.caption(
                        "These values were retrieved automatically "
                        "through the configured platform API."
                    )

                    # ====================================================
                    # CALCULATED METRICS
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 📈 SocialPulse Metrics"
                    )

                    metrics = result[
                        "calculated_metrics"
                    ]

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Engagement Rate",
                            f"{metrics['engagement_rate']:.2f}%"
                        )

                    with col2:

                        st.metric(
                            "Virality Score",
                            f"{metrics['virality_score']:.2f}"
                        )

                    with col3:

                        st.metric(
                            "Virality Coefficient",
                            f"{metrics['viral_coefficient']:.4f}"
                        )

                    st.write("")

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Like Rate",
                            f"{metrics['like_rate']:.2f}%"
                        )

                    with col2:

                        st.metric(
                            "Share Rate",
                            f"{metrics['share_rate']:.2f}%"
                        )

                    with col3:

                        st.metric(
                            "Comment Rate",
                            f"{metrics['comment_rate']:.2f}%"
                        )

                    # ====================================================
                    # CLASSIFICATION
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 🎯 Post Classification"
                    )

                    classification = result[
                        "classification"
                    ]

                    col1, col2 = st.columns(2)

                    with col1:

                        engagement_level = (
                            classification[
                                "engagement_level"
                            ]
                        )

                        st.metric(
                            "Engagement Level",
                            engagement_level
                        )

                    with col2:

                        if classification[
                            "engagement_anomaly"
                        ]:

                            st.warning(
                                "⚠️ Engagement anomaly detected"
                            )

                        else:

                            st.success(
                                "✓ No engagement anomaly detected"
                            )

                    # ====================================================
                    # SOCIALPULSE COMPARISON
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 📊 Comparison with SocialPulse"
                    )

                    comparison = result[
                        "comparison"
                    ]

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Comparable Posts",
                            f"{comparison['comparison_posts']:,}"
                        )

                    with col2:

                        st.metric(
                            "Median Engagement",
                            f"{comparison['median_engagement']:.2f}%"
                        )

                    st.write("")

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Median Virality",
                            f"{comparison['median_virality']:.2f}"
                        )

                    with col2:

                        st.metric(
                            "Engagement Difference",
                            f"{comparison['engagement_difference']:+.2f}%"
                        )

                    st.write("")

                    col1, col2 = st.columns(2)

                    with col1:

                        if comparison[
                            "engagement_vs_median_percent"
                        ] is not None:

                            st.metric(
                                "Engagement vs Median",
                                f"{comparison['engagement_vs_median_percent']:.1f}%"
                            )

                    with col2:

                        if comparison[
                            "virality_vs_median_percent"
                        ] is not None:

                            st.metric(
                                "Virality vs Median",
                                f"{comparison['virality_vs_median_percent']:.1f}%"
                            )

                    st.write("")

                    st.metric(
                        "Virality Difference",
                        f"{comparison['virality_difference']:+.2f}"
                    )

                    # ====================================================
                    # ENGAGEMENT BREAKDOWN
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 📊 Engagement Breakdown"
                    )

                    chart_df = pd.DataFrame({
                        "Metric": [
                            "Likes",
                            "Shares",
                            "Comments"
                        ],
                        "Count": [
                            raw["likes"],
                            raw["shares"],
                            raw["comments"]
                        ]
                    })

                    fig = px.bar(
                        chart_df,
                        x="Metric",
                        y="Count",
                        title="Post Engagement Breakdown",
                        text_auto=True
                    )

                    fig.update_layout(
                        xaxis_title="Engagement Type",
                        yaxis_title="Count"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                    # ====================================================
                    # PERFORMANCE SUMMARY
                    # ====================================================

                    st.divider()

                    st.markdown(
                        "## 📝 Performance Summary"
                    )

                    engagement_difference = (
                        comparison[
                            "engagement_difference"
                        ]
                    )

                    virality_difference = (
                        comparison[
                            "virality_difference"
                        ]
                    )

                    if engagement_difference > 0:

                        engagement_message = (
                            "The post has a higher engagement rate "
                            "than the SocialPulse median."
                        )

                    elif engagement_difference < 0:

                        engagement_message = (
                            "The post has a lower engagement rate "
                            "than the SocialPulse median."
                        )

                    else:

                        engagement_message = (
                            "The post's engagement rate is equal "
                            "to the SocialPulse median."
                        )

                    if virality_difference > 0:

                        virality_message = (
                            "Its virality score is higher than "
                            "the SocialPulse median."
                        )

                    elif virality_difference < 0:

                        virality_message = (
                            "Its virality score is lower than "
                            "the SocialPulse median."
                        )

                    else:

                        virality_message = (
                            "Its virality score is equal to "
                            "the SocialPulse median."
                        )

                    st.info(
                        f"**Engagement:** {engagement_message}\n\n"
                        f"**Virality:** {virality_message}"
                    )

                    # ====================================================
                    # FORMULAS
                    # ====================================================

                    with st.expander(
                        "🧮 View Calculation Formulas"
                    ):

                        st.markdown(
                            """
                            **Engagement Rate**

                            `(Likes + Shares + Comments) / Views × 100`

                            **Like Rate**

                            `Likes / Views × 100`

                            **Share Rate**

                            `Shares / Views × 100`

                            **Comment Rate**

                            `Comments / Views × 100`

                            **Virality Coefficient**

                            `0.60 × (Shares / Views) + 0.20 × (Comments / Views) + 0.20 × (Likes / Views)`

                            **Virality Score**

                            `Virality Coefficient × 100`
                            """
                        )

            except requests.exceptions.Timeout:

                st.error(
                    "❌ The request timed out. "
                    "Please try again."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to the SocialPulse backend."
                )

            except Exception as e:

                st.error(
                    f"❌ Unable to analyze the post: {e}"
                )
# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "SocialPulse • Data-Driven Social Media Engagement Intelligence System"
)