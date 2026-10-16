"""
SocialPulse — Data-Driven Social Media Engagement Intelligence System
Streamlit UI with five tabs, designed to integrate with the existing FastAPI backend.

Run:
    pip install streamlit requests pandas plotly
    streamlit run app.py

Configuration:
    Set SOCIALPULSE_API_URL to your FastAPI base URL (default: http://localhost:8000).
    This UI calls existing endpoints and avoids fabricating post or recommendation records.
"""
from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Keep this configurable so an existing deployment can retain its backend URL.
API_BASE_URL = os.getenv("SOCIALPULSE_API_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = (4, 25)

ICON_PATH = os.path.join(os.path.dirname(__file__), "social_sense_icon.jpg")

st.set_page_config(
    page_title="Social Sense | Engagement Intelligence",

    page_icon=ICON_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #0b1020; color: #edf2ff; }
    [data-testid="stHeader"] { background: rgba(11,16,32,.88); }
    [data-testid="stSidebar"] { background: #10172a; border-right: 1px solid #27324b; }
    [data-testid="stMetric"] {
        background: #121b30; border: 1px solid #293650; border-radius: 14px;
        padding: 16px 18px;
    }
    [data-testid="stMetricLabel"] { color: #a8b6d3; }
    [data-testid="stMetricValue"] { color: #f3f6ff; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #293650 !important; border-radius: 14px;
    }
    .eyebrow { color:#7dd3fc; font-size:.78rem; letter-spacing:.13em; text-transform:uppercase; }
    .muted { color:#a8b6d3; }
    .hero {
        background: linear-gradient(120deg,#141d35,#15152d);
        border: 1px solid #293650; border-radius: 18px; padding: 28px;
        margin: 4px 0 20px 0;
    }
    .hero h1 { margin: 5px 0 8px 0; font-size: clamp(3.2rem, 7vw, 6.2rem); line-height: 1.02; font-weight: 800; letter-spacing: -0.045em; }
    .brand-title { font-size: 1.75rem; font-weight: 800; letter-spacing: -0.035em; color: #f3f6ff; line-height: 1.05; }
    .brand-subtitle { font-size: .78rem; color: #a8b6d3; margin-top: 5px; }
    .pill { display:inline-block; padding:4px 10px; border-radius:99px;
        background:#202b48; color:#c4b5fd; font-size:.78rem; margin-right:6px; }
    div.stButton > button[kind="primary"] {
        background: #7565e8; border: 1px solid #9185ff; color:white;
    }
    div.stButton > button { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- API helpers ----------
def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Return decoded JSON or raise a useful error."""
    response = requests.get(
        f"{API_BASE_URL}{path}", params=params, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    if not response.content:
        return {}
    return response.json()


def api_post(path: str, payload: dict[str, Any]) -> Any:
    response = requests.post(
        f"{API_BASE_URL}{path}", json=payload, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    if not response.content:
        return {}
    return response.json()


def show_api_error(error: Exception, endpoint: str) -> None:
    st.warning(
        f"Could not load `{endpoint}` from the API at `{API_BASE_URL}`. "
        "Check that the FastAPI backend is running and that its configured URL is correct. "
        f"Details: {error}"
    )


def as_frame(payload: Any) -> pd.DataFrame:
    """Convert common API response shapes into a DataFrame without inventing rows."""
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        for key in ("data", "results", "items", "posts", "records", "recommendations", "comments"):
            value = payload.get(key)
            if isinstance(value, list):
                return pd.DataFrame(value)
        # Some endpoints return a single record.
        if payload and all(not isinstance(v, (list, dict)) for v in payload.values()):
            return pd.DataFrame([payload])
    return pd.DataFrame()


def first_value(data: Any, *keys: str, default: Any = None) -> Any:
    if isinstance(data, dict):
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
    return default


def numeric_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for col in candidates:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            return col
        if col in df.columns:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().any():
                df[col] = converted
                return col
    return None


def find_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    lower_map = {str(c).lower().strip().replace(" ", "_"): c for c in df.columns}
    for candidate in candidates:
        normalized = candidate.lower().strip().replace(" ", "_")
        if normalized in lower_map:
            return lower_map[normalized]
    return None


def show_table(df: pd.DataFrame, key: str, height: int = 360) -> None:
    if df.empty:
        st.info("No records were returned by the backend for this view.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True, height=height, key=key)


def api_options(path: str, fallback: list[str] | None = None) -> list[str]:
    try:
        payload = api_get(path)
        if isinstance(payload, dict):
            values = first_value(payload, "data", "items", "values", "platforms", "regions", "content_types", "hashtags")
            if isinstance(values, list):
                return [str(v) for v in values if v is not None]
        if isinstance(payload, list):
            return [str(v) for v in payload if v is not None]
    except Exception:
        pass
    return fallback or []


def safe_pct(value: Any) -> str:
    try:
        v = float(value)
        return f"{v:.2f}%"
    except (TypeError, ValueError):
        return "—"


def page_title(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="eyebrow">SOCIALPULSE / ANALYTICS</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def call_table_endpoint(endpoint: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    payload = api_get(endpoint, params=params)
    return as_frame(payload)


# ---------- Navigation ----------
PAGES = [
    "Home",
    "Social Media Post Analyzer",
    "Virality Calculator",
    "Audience Insights",
    "Content Recommendations",
]
if "socialpulse_page" not in st.session_state:
    st.session_state.socialpulse_page = "Home"


def go_to_analyzer() -> None:
    st.session_state.socialpulse_page = "Social Media Post Analyzer"


with st.sidebar:
    if os.path.exists(ICON_PATH):
        st.image(ICON_PATH, width=108)
    st.markdown('<div class="brand-title">Social Sense</div><div class="brand-subtitle">Engagement intelligence</div>', unsafe_allow_html=True)
    st.divider()
    selected_page = st.radio(
        "Navigation",
        PAGES,
        index=PAGES.index(st.session_state.socialpulse_page),
        key="socialpulse_nav",
        label_visibility="collapsed",
    )
    st.session_state.socialpulse_page = selected_page

page = st.session_state.socialpulse_page

# ---------- Home ----------
if page == "Home":
    # Note: The original app.py was not available in this session. This is a standalone
    # Home view; merge the new tabs into the existing Home file to preserve it exactly.
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">SOCIAL MEDIA ENGAGEMENT INTELLIGENCE</div>
          <h1>Social Sense</h1>
          <h3 style="font-weight:500; margin-top:8px;">Understand what makes content perform.</h3>
          <p class="muted">Explore engagement, audience sentiment, virality and historical content patterns in one workspace.</p>
          <span class="pill">Analytics</span><span class="pill">Audience insights</span><span class="pill">Content strategy</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Your social performance, at a glance")
        st.write("Use the analytics tools to explore actual records from your configured SocialPulse API.")
  
        if st.button("Analyze a Post", key="home_analyze_post"):
            st.session_state.socialpulse_page = "Social Media Post Analyzer"
            st.rerun()

    with right:
        st.markdown("#### Workspace")
        st.markdown("- **Post Analyzer** — inspect a supported post URL")
        st.markdown("- **Virality Calculator** — rank posts using backend data")
        st.markdown("- **Audience Insights** — review sentiment distribution")
        st.markdown("- **Content Recommendations** — discover historical patterns")
    try:
        summary = api_get("/api/summary")
        if isinstance(summary, dict):
            st.subheader("Performance overview")
            metrics = [(k, v) for k, v in summary.items() if not isinstance(v, (dict, list))]
            if metrics:
                cols = st.columns(min(4, len(metrics)))
                for i, (label, value) in enumerate(metrics[:4]):
                    cols[i].metric(str(label).replace("_", " ").title(), value if value is not None else "—")
    except Exception as exc:
        with st.expander("Summary API status"):
            show_api_error(exc, "/api/summary")

# ---------- Post Analyzer ----------

elif page == "Social Media Post Analyzer":
    page_title(
        "Social Media Post Analyzer",
        "Analyze a supported post and inspect the metrics returned by your backend."
    )

    with st.container(border=True):
        post_url = st.text_input(
            "Social media post URL",
            placeholder="https://www.youtube.com/watch?v=…",
            key="analyzer_url",
        )
        analyze = st.button(
            "Analyze Post",
            type="primary",
            use_container_width=False
        )

    if analyze:
        if not post_url.strip():
            st.error("Enter a post URL to analyze.")

        elif not post_url.strip().lower().startswith(("https://", "http://")):
            st.error("Enter a valid URL beginning with http:// or https://.")

        else:
            with st.spinner("Analyzing post…"):
                try:
                    result = api_post(
                        "/api/analyze-post",
                        {"url": post_url.strip()}
                    )
                    st.session_state["socialpulse_last_analysis"] = result

                except requests.HTTPError as exc:
                    status = (
                        exc.response.status_code
                        if exc.response is not None
                        else "unknown"
                    )
                    st.error(
                        f"The analyzer API returned HTTP {status}. "
                        "Confirm the URL is supported and accessible."
                    )

                except requests.RequestException as exc:
                    st.error(f"Could not reach the analyzer API. {exc}")

                except ValueError:
                    st.error("The analyzer returned a response that was not valid JSON.")

                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
    
    result = st.session_state.get("socialpulse_last_analysis")

    if result:
        st.subheader("Analysis Results")

        if isinstance(result, dict):
            post = result.get("post", {})
            raw = result.get("raw_metrics", {})
            calculated = result.get("calculated_metrics", {})
            classification = result.get("classification", {})
            comparison = result.get("comparison", {})

            # Post information
            st.markdown("### Post Details")
            st.write("**Title:**", post.get("title", "Not available"))
            st.write("**Platform:**", post.get("platform", "Not available"))
            st.write("**Published:**", post.get("published_at", "Not available"))

            post_url = post.get("url")
            if post_url:
                st.markdown(f"[Open original post]({post_url})")

            st.divider()

            # Main metrics
            st.markdown("### Engagement Overview")

            def format_number(value):
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    return f"{value:,.2f}".rstrip("0").rstrip(".")
                return value if value is not None else "—"

            metrics = [
                ("Views", raw.get("views")),
                ("Likes", raw.get("likes")),
                ("Comments", raw.get("comments")),
                ("Shares", raw.get("shares")),
                ("Engagement Rate", calculated.get("engagement_rate")),
                ("Virality Score", calculated.get("virality_score")),
            ]

            cols = st.columns(3)

            for i, (label, value) in enumerate(metrics):
                display = format_number(value)

                if "Rate" in label and value is not None:
                    display = f"{format_number(value)}%"

                cols[i % 3].metric(label, display)

            st.divider()

            # Classification
            st.markdown("### Engagement Classification")

            col1, col2 = st.columns(2)

            col1.metric(
                "Engagement Level",
                classification.get("engagement_level", "—")
            )

            anomaly = classification.get("engagement_anomaly")

            col2.metric(
                "Engagement Anomaly",
                "Yes" if anomaly is True
                else "No" if anomaly is False
                else "—"
            )

            st.divider()

            # Comparison against other posts
            st.markdown("### Performance Comparison")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Comparison Posts",
                format_number(comparison.get("comparison_posts"))
            )

            c2.metric(
                "Median Engagement",
                f"{format_number(comparison.get('median_engagement'))}%"
                if comparison.get("median_engagement") is not None
                else "—"
            )

            c3.metric(
                "Median Virality",
                format_number(comparison.get("median_virality"))
            )

            c4, c5 = st.columns(2)

            c4.metric(
                "Engagement Difference",
                format_number(comparison.get("engagement_difference"))
            )

            c5.metric(
                "Virality Difference",
                format_number(comparison.get("virality_difference"))
            )

            # Full response for debugging
            with st.expander("Full API Response"):
                st.json(result)

        else:
            st.error("The API response is not in the expected JSON format.")
            st.json(result)

    else:
        st.info("Enter a post URL and click Analyze Post to begin.")


# ---------- Virality Calculator ----------
elif page == "Virality Calculator":
    page_title("Virality Calculator", "Calculate a score when supported by your API and explore the highest-scoring historical posts.")
    st.subheader("Calculate Virality")
    st.caption("This form submits the supplied values to the existing API only if a compatible calculation endpoint is available.")
    with st.container(border=True):
        a, b, c, d = st.columns(4)
        views = a.number_input("Views", min_value=0, value=0, step=100)
        likes = b.number_input("Likes", min_value=0, value=0, step=10)
        comments = c.number_input("Comments", min_value=0, value=0, step=5)
        shares = d.number_input("Shares", min_value=0, value=0, step=5)
        if st.button("Calculate Virality", type="primary"):
            total_engagement = likes + comments + shares
            st.metric("Engagement count", f"{total_engagement:,}")
            if views > 0:
                st.metric("Engagement per view", f"{total_engagement / views * 100:.2f}%")
            else:
                st.info("Engagement per view cannot be calculated unless views are greater than zero.")
            st.caption("These are transparent arithmetic metrics, not the project's virality score. The project's score is not inferred or replaced here.")
    st.divider()
    st.subheader("Top Viral Posts")
    try:
        df = call_table_endpoint("/api/top-posts")
        if df.empty:
            st.info("The top-posts endpoint returned no post records.")
        else:
            df = df.drop_duplicates()
            score_col = find_column(df, ("virality_score", "virality", "viral_score", "score"))
            search = st.text_input("Search by hashtag or post ID", key="viral_search")
            platform_col = find_column(df, ("platform", "social_platform"))
            type_col = find_column(df, ("content_type", "type", "media_type"))
            f1, f2, f3 = st.columns(3)
            if platform_col:
                opts = ["All"] + sorted(df[platform_col].dropna().astype(str).unique().tolist())
                p = f1.selectbox("Platform", opts, key="viral_platform")
                if p != "All":
                    df = df[df[platform_col].astype(str) == p]
            if type_col:
                opts = ["All"] + sorted(df[type_col].dropna().astype(str).unique().tolist())
                t = f2.selectbox("Content type", opts, key="viral_type")
                if t != "All":
                    df = df[df[type_col].astype(str) == t]
            sort_col = score_col or find_column(df, ("engagement_rate", "engagement"))
            sort_choice = f3.selectbox("Sort by", [c for c in (score_col, find_column(df, ("engagement_rate", "engagement"))) if c], key="viral_sort") if any((score_col, find_column(df, ("engagement_rate", "engagement")))) else None
            if search:
                search_cols = [c for c in (find_column(df, ("hashtag", "hashtags")), find_column(df, ("post_id", "id"))) if c]
                if search_cols:
                    mask = pd.Series(False, index=df.index)
                    for col in search_cols:
                        mask |= df[col].astype(str).str.contains(search, case=False, na=False)
                    df = df[mask]
            if sort_choice:
                df[sort_choice] = pd.to_numeric(df[sort_choice], errors="coerce")
                df = df.sort_values(sort_choice, ascending=False, na_position="last")
            top_n = st.selectbox("Rows to display", [10, 25, 50, 100], index=1, key="viral_top_n")
            if score_col and not df.empty:
                chart_df = df.head(top_n).copy()
                label_col = find_column(chart_df, ("post_id", "id", "hashtag")) or chart_df.columns[0]
                chart_df[score_col] = pd.to_numeric(chart_df[score_col], errors="coerce")
                chart_df = chart_df.dropna(subset=[score_col])
                if not chart_df.empty:
                    fig = px.bar(chart_df.sort_values(score_col), x=score_col, y=label_col, orientation="h",
                                 title="Top posts by virality score", hover_data=list(chart_df.columns))
                    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=max(360, 28 * len(chart_df)))
                    st.plotly_chart(fig, use_container_width=True)
            show_table(df.head(top_n), "viral_table")
    except Exception as exc:
        show_api_error(exc, "/api/top-posts")

# ---------- Audience Insights ----------
elif page == "Audience Insights":
    page_title("Audience Insights", "Understand positive, neutral, and negative audience reactions in the sentiment dataset.")
    st.subheader("Sentiment Summary")
    # These are the explicitly supplied baseline statistics; clearly labelled as baseline.
    metrics = [
        ("Comments Analyzed", "36,793"),
        ("Positive Sentiment", "42.86%"),
        ("Neutral Sentiment", "34.71%"),
        ("Negative Sentiment", "22.42%"),
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)
    st.caption("Baseline values supplied in the project brief. They remain a baseline until recalculated from updated source data.")
    st.divider()
    st.subheader("Audience Sentiment Distribution")
    sentiment_df = pd.DataFrame({"Sentiment": ["Positive", "Neutral", "Negative"], "Percentage": [42.86, 34.71, 22.42]})
    fig = px.pie(sentiment_df, names="Sentiment", values="Percentage", hole=0.58,
                 color="Sentiment", color_discrete_map={"Positive": "#34d399", "Neutral": "#60a5fa", "Negative": "#fb7185"})
    fig.update_traces(textposition="inside", textinfo="label+percent", hovertemplate="%{label}: %{value:.2f}%<extra></extra>")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend_title_text="Sentiment", margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)
    st.info("Sentiment analysis provides an overall view of audience reaction within the analyzed comment dataset.")
    st.divider()
    st.subheader("Sentiment Details")
    try:
        payload = api_get("/api/sentiment")
        df = as_frame(payload)
        if df.empty and isinstance(payload, dict):
            st.write("The sentiment endpoint returned aggregated data rather than individual comment records:")
            st.json(payload)
        elif not df.empty:
            sentiment_col = find_column(df, ("sentiment", "sentiment_label", "label", "polarity"))
            if sentiment_col:
                labels = ["All"] + sorted(df[sentiment_col].dropna().astype(str).unique().tolist())
                selected = st.selectbox("Filter sentiment", labels)
                if selected != "All":
                    df = df[df[sentiment_col].astype(str) == selected]
            search = st.text_input("Search sentiment details", key="sentiment_search")
            if search:
                mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
                df = df[mask]
            show_table(df, "sentiment_table")
    except Exception as exc:
        show_api_error(exc, "/api/sentiment")

# ---------- Content Recommendations ----------
elif page == "Content Recommendations":
    page_title("Content Recommendations", "Discover content patterns that have performed well historically in SocialPulse.")
    st.subheader("Choose Your Target")
    try:
        platforms = api_options("/api/platforms")
        content_types = api_options("/api/content-types")
        hashtags = api_options("/api/hashtags")
    except Exception:
        platforms, content_types, hashtags = [], [], []
    with st.container(border=True):
        c1, c2 = st.columns(2)
        platform_choice = c1.selectbox("Platform", ["All"] + platforms, key="rec_platform")
        type_choice = c2.selectbox("Content type", ["All"] + content_types, key="rec_type")
        hashtag_choice = st.selectbox("Hashtag", ["All"] + hashtags, key="rec_hashtag")
        target_metric = st.selectbox("Target metric", ["Virality score", "Engagement rate"], key="rec_metric")
        apply = st.button("Generate Recommendations", type="primary")
        reset = st.button("Reset Filters")
        if reset:
            for k in ("rec_platform", "rec_type", "rec_hashtag", "rec_metric"):
                st.session_state.pop(k, None)
            st.rerun()
    params: dict[str, Any] = {}
    if platform_choice != "All":
        params["platform"] = platform_choice
    if type_choice != "All":
        params["content_type"] = type_choice
    if hashtag_choice != "All":
        params["hashtag"] = hashtag_choice
    params["target_metric"] = "virality_score" if target_metric == "Virality score" else "engagement_rate"

    st.divider()
    st.subheader("Recommended Content Patterns")
    try:
        # Pass current UI filters through to the existing recommendation endpoint.
        payload = api_get("/api/recommendations", params=params)
        rec_df = as_frame(payload)
        if rec_df.empty:
            # Preserve a returned aggregate response rather than fabricating recommendation rows.
            if isinstance(payload, dict) and payload:
                st.json(payload)
            else:
                st.info("No recommendations were returned for the selected filters.")
        else:
            rec_df = rec_df.drop_duplicates()
            score_col = find_column(rec_df, ("virality_score", "avg_virality_score", "average_virality", "score"))
            engagement_col = find_column(rec_df, ("engagement_rate", "avg_engagement_rate", "average_engagement_rate"))
            count_col = find_column(rec_df, ("post_count", "supporting_posts", "count", "num_posts"))
            k1, k2, k3 = st.columns(3)
            k1.metric("Recommendations", f"{len(rec_df):,}")
            k2.metric("Top Virality", f"{pd.to_numeric(rec_df[score_col], errors='coerce').max():.2f}" if score_col else "Not returned")
            k3.metric("Top Engagement", safe_pct(pd.to_numeric(rec_df[engagement_col], errors="coerce").max()) if engagement_col else "Not returned")
            if score_col or engagement_col:
                y = score_col if target_metric == "Virality score" and score_col else engagement_col or score_col
                labels = [c for c in (find_column(rec_df, ("content_type", "type")), find_column(rec_df, ("hashtag", "hashtags")), find_column(rec_df, ("platform",))) if c]
                chart_df = rec_df.copy()
                chart_df[y] = pd.to_numeric(chart_df[y], errors="coerce")
                chart_df = chart_df.dropna(subset=[y]).sort_values(y, ascending=False).head(15)
                if not chart_df.empty:
                    chart_df["Pattern"] = chart_df[labels].astype(str).agg(" · ".join, axis=1) if labels else chart_df.index.astype(str)
                    fig = px.bar(chart_df.sort_values(y), x=y, y="Pattern", orientation="h",
                                 title=f"Recommended patterns by {target_metric.lower()}", hover_data=list(chart_df.columns))
                    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=max(360, 28 * len(chart_df)))
                    st.plotly_chart(fig, use_container_width=True)
            st.markdown("#### Recommendation Details")
            search = st.text_input("Search recommendations", key="rec_search")
            if search:
                mask = rec_df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
                rec_df = rec_df[mask]
            sort_candidates = [c for c in (score_col, engagement_col, count_col) if c and c in rec_df.columns]
            if sort_candidates:
                sort_by = st.selectbox("Sort recommendations by", sort_candidates, key="rec_sort")
                rec_df[sort_by] = pd.to_numeric(rec_df[sort_by], errors="coerce")
                rec_df = rec_df.sort_values(sort_by, ascending=False, na_position="last")
            page_size = st.selectbox("Rows per page", [10, 25, 50], key="rec_page_size")
            page_count = max(1, (len(rec_df) + page_size - 1) // page_size)
            current_page = st.number_input("Page", min_value=1, max_value=page_count, value=1, step=1, key="rec_page")
            start = (current_page - 1) * page_size
            show_table(rec_df.iloc[start:start + page_size], "recommendation_table")
    except Exception as exc:
        show_api_error(exc, "/api/recommendations")
    st.caption("Recommendations are based on historical performance in the SocialPulse dataset. They represent observed content patterns and are not guaranteed future outcomes.")

st.markdown("---")
st.caption("Social Sense · Data-driven engagement intelligence")
