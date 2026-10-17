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
    """Extract readable selectbox values from common API response shapes."""
    endpoint = path.rstrip("/").split("/")[-1].lower()
    if "platform" in endpoint:
        value_keys = ("platform", "platform_name", "name", "value", "label")
        wrapper_keys = ("platforms", "data", "items", "values", "results")
    elif "content-type" in endpoint or "content_types" in endpoint:
        value_keys = ("content_type", "content type", "type", "name", "value", "label")
        wrapper_keys = ("content_types", "contentTypes", "types", "data", "items", "values", "results")
    elif "hashtag" in endpoint:
        value_keys = ("hashtag", "tag", "name", "value", "label")
        wrapper_keys = ("hashtags", "data", "items", "values", "results")
    elif "region" in endpoint:
        value_keys = ("region", "name", "value", "label")
        wrapper_keys = ("regions", "data", "items", "values", "results")
    else:
        value_keys = ("name", "value", "label")
        wrapper_keys = ("data", "items", "values", "results")

    def extract(value: Any) -> list[str]:
        found: list[str] = []
        if value is None:
            return found
        if isinstance(value, str):
            clean = value.strip()
            if clean:
                found.append(clean)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            found.append(str(value))
        elif isinstance(value, dict):
            normalized_keys = {
                str(key).strip().lower().replace(" ", "_"): key for key in value
            }
            matched_value = False
            for candidate in value_keys:
                normalized_candidate = candidate.strip().lower().replace(" ", "_")
                original_key = normalized_keys.get(normalized_candidate)
                if original_key is not None and not isinstance(value[original_key], (dict, list)):
                    found.extend(extract(value[original_key]))
                    matched_value = True
                    break
            if not matched_value:
                # Some endpoints wrap arrays or return mappings like {"Instagram": 1200}.
                for candidate in wrapper_keys:
                    original_key = normalized_keys.get(candidate.strip().lower().replace(" ", "_"))
                    if original_key is not None:
                        found.extend(extract(value[original_key]))
                        matched_value = True
                        break
            if not matched_value:
                for key, item in value.items():
                    if isinstance(item, (int, float)) and not isinstance(item, bool):
                        found.append(str(key))
                    elif isinstance(item, (list, dict)):
                        found.extend(extract(item))
        elif isinstance(value, list):
            for item in value:
                found.extend(extract(item))
        # Keep first-seen order and remove duplicates.
        return list(dict.fromkeys(found))

    try:
        values = extract(api_get(path))
        if values:
            return values
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
    # Keep the navigation widget's keyed value in sync with the page state.
    st.session_state["socialpulse_page"] = "Social Media Post Analyzer"
    st.session_state["socialpulse_nav"] = "Social Media Post Analyzer"


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
  
        st.button(
            "Analyze a Post",
            key="home_analyze_post",
            type="primary",
            on_click=go_to_analyzer,
        )

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
    page_title(
        "Content Recommendations",
        "Discover content patterns that have performed well historically in SocialPulse.",
    )
    st.subheader("Choose Your Target")

    platforms = api_options(
        "/api/platforms",
        fallback=["Instagram", "TikTok", "YouTube", "Twitter"],
    )
    content_types = api_options(
        "/api/content-types",
        fallback=["Post", "Reel", "Story", "Stream", "Video", "Image", "Text"],
    )
    hashtags = api_options("/api/hashtags", fallback=[])

    def reset_recommendation_filters() -> None:
        for key in (
            "rec_platform", "rec_type", "rec_hashtags", "rec_metric",
            "rec_search", "rec_sort", "rec_page", "rec_page_size",
            "rec_applied_filters", "rec_results", "rec_api_error",
        ):
            st.session_state.pop(key, None)

    with st.container(border=True):
        with st.form("recommendation_filter_form"):
            c1, c2 = st.columns(2)
            platform_choice = c1.selectbox(
                "Platform", ["All"] + platforms, key="rec_platform",
                help="Choose All platforms or one specific platform.",
            )
            type_choice = c2.selectbox(
                "Content type", ["All"] + content_types, key="rec_type",
                help="Choose the type of post you want to explore.",
            )
            hashtag_choices = st.multiselect(
                "Hashtags", hashtags, key="rec_hashtags",
                placeholder="Choose one or more hashtags",
                help="Select multiple hashtags to narrow the results.",
            )
            target_metric = st.selectbox(
                "Rank recommendations by",
                ["Virality score", "Engagement rate"],
                key="rec_metric",
            )
            submitted = st.form_submit_button(
                "Generate Recommendations", type="primary", use_container_width=True
            )
        st.button(
            "Reset Filters", key="reset_recommendation_filters_button",
            on_click=reset_recommendation_filters,
        )

    if submitted:
        request_params: dict[str, Any] = {}
        if platform_choice != "All":
            # The existing recommendation API supports platform filtering.
            request_params["platform"] = platform_choice

        try:
            with st.spinner("Loading recommendations from the SocialPulse API…"):
                payload = api_get("/api/recommendations", params=request_params)
            raw_df = as_frame(payload)
            st.session_state["rec_results"] = raw_df.to_dict(orient="records")
            st.session_state["rec_api_payload"] = payload if raw_df.empty else None
            st.session_state["rec_applied_filters"] = {
                "platform": platform_choice,
                "content_type": type_choice,
                "hashtags": hashtag_choices,
                "target_metric": target_metric,
            }
            st.session_state.pop("rec_api_error", None)
            st.session_state["rec_page"] = 1
        except requests.RequestException as exc:
            st.session_state["rec_api_error"] = str(exc)
            st.session_state.pop("rec_results", None)
            st.session_state.pop("rec_applied_filters", None)

    if "rec_api_error" in st.session_state:
        st.error(f"Could not load recommendations from /api/recommendations: {st.session_state['rec_api_error']}")
    elif "rec_applied_filters" not in st.session_state:
        st.info("Choose your filters and click **Generate Recommendations** to load results.")
    else:
        applied = st.session_state["rec_applied_filters"]
        rec_df = pd.DataFrame(st.session_state.get("rec_results", []))

        st.divider()
        st.subheader("Recommended Content Patterns")

        if rec_df.empty:
            payload = st.session_state.get("rec_api_payload")
            if isinstance(payload, dict) and payload:
                st.warning("The API returned a response, but no recommendation rows could be extracted.")
                with st.expander("API response details"):
                    st.json(payload)
            else:
                st.info("No recommendations were returned for the selected platform.")
        else:
            rec_df = rec_df.drop_duplicates().copy()
            platform_col = find_column(rec_df, ("platform", "social_platform"))
            type_col = find_column(rec_df, ("content_type", "type", "media_type"))
            hashtag_col = find_column(rec_df, ("hashtag", "hashtags", "tag"))
            virality_col = find_column(rec_df, (
                "median_virality", "virality_score", "avg_virality_score",
                "average_virality", "mean_virality", "virality", "viral_score", "score",
            ))
            engagement_col = find_column(rec_df, (
                "median_engagement", "engagement_rate", "avg_engagement_rate",
                "average_engagement_rate", "mean_engagement", "engagement",
            ))
            count_col = find_column(rec_df, (
                "post_count", "supporting_posts", "count", "num_posts", "total_posts",
            ))

            # Apply filters locally when the recommendation endpoint does not expose
            # content-type or hashtag query parameters.
            if applied.get("content_type") != "All" and type_col:
                rec_df = rec_df[
                    rec_df[type_col].astype(str).str.casefold()
                    == str(applied["content_type"]).casefold()
                ]
            selected_tags = applied.get("hashtags") or []
            if selected_tags and hashtag_col:
                tag_text = rec_df[hashtag_col].fillna("").astype(str).str.casefold()
                tag_mask = pd.Series(False, index=rec_df.index)
                for tag in selected_tags:
                    normalized_tag = str(tag).strip().lstrip("#").casefold()
                    tag_mask |= tag_text.str.contains(
                        rf"(?<![A-Za-z0-9_])#?{__import__('re').escape(normalized_tag)}(?![A-Za-z0-9_])",
                        regex=True,
                        na=False,
                    )
                rec_df = rec_df[tag_mask]

            # Some APIs return recommendations grouped without a platform column;
            # the selected platform has already been applied through the API request.
            if rec_df.empty:
                st.info("No recommendation patterns match the selected content type and hashtag filters. Try broadening your selection.")
            else:
                selected_metric_col = virality_col if applied["target_metric"] == "Virality score" else engagement_col
                if selected_metric_col is None:
                    selected_metric_col = virality_col or engagement_col
                if selected_metric_col:
                    rec_df[selected_metric_col] = pd.to_numeric(rec_df[selected_metric_col], errors="coerce")
                    rec_df = rec_df.sort_values(selected_metric_col, ascending=False, na_position="last")

                k1, k2, k3 = st.columns(3)
                k1.metric("Recommendations", f"{len(rec_df):,}")
                if virality_col:
                    max_virality = pd.to_numeric(rec_df[virality_col], errors="coerce").max()
                    k2.metric("Top Virality", f"{max_virality:.2f}" if pd.notna(max_virality) else "—")
                else:
                    k2.metric("Top Virality", "Not returned")
                if engagement_col:
                    max_engagement = pd.to_numeric(rec_df[engagement_col], errors="coerce").max()
                    k3.metric("Top Engagement", safe_pct(max_engagement) if pd.notna(max_engagement) else "—")
                else:
                    k3.metric("Top Engagement", "Not returned")

                st.markdown("#### Performance by Content Pattern")
                if selected_metric_col:
                    chart_df = rec_df.copy()
                    chart_df = chart_df.dropna(subset=[selected_metric_col]).head(15).copy()
                    label_cols = [
                        col for col in (platform_col, type_col, hashtag_col)
                        if col and col in chart_df.columns
                    ]
                    if not chart_df.empty:
                        if label_cols:
                            chart_df["Pattern"] = chart_df[label_cols].fillna("Unknown").astype(str).agg(" · ".join, axis=1)
                        else:
                            chart_df["Pattern"] = [f"Pattern {i + 1}" for i in range(len(chart_df))]
                        chart_df = chart_df.sort_values(selected_metric_col, ascending=True)
                        fig = px.bar(
                            chart_df, x=selected_metric_col, y="Pattern", orientation="h",
                            title=f"Top patterns by {applied['target_metric'].lower()}",
                            hover_data=[c for c in (virality_col, engagement_col, count_col) if c and c in chart_df.columns],
                        )
                        fig.update_layout(
                            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            height=max(360, 32 * len(chart_df)),
                            yaxis_title="Content pattern",
                            xaxis_title=applied["target_metric"],
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"The API did not return numeric values for {applied['target_metric'].lower()}.")
                else:
                    st.info("The recommendation response does not include a virality or engagement score to chart.")

                st.markdown("#### Recommendation Details")
                search = st.text_input("Search recommendations", key="rec_search")
                table_df = rec_df.copy()
                if search.strip():
                    mask = table_df.astype(str).apply(
                        lambda col: col.str.contains(search.strip(), case=False, na=False)
                    ).any(axis=1)
                    table_df = table_df[mask]

                sort_candidates = [c for c in (virality_col, engagement_col, count_col) if c and c in table_df.columns]
                if sort_candidates:
                    default_sort = selected_metric_col if selected_metric_col in sort_candidates else sort_candidates[0]
                    sort_by = st.selectbox(
                        "Sort recommendations by", sort_candidates,
                        index=sort_candidates.index(default_sort), key="rec_sort",
                    )
                    table_df[sort_by] = pd.to_numeric(table_df[sort_by], errors="coerce")
                    table_df = table_df.sort_values(sort_by, ascending=False, na_position="last")
                if not table_df.empty:
                    table_df.insert(0, "Rank", range(1, len(table_df) + 1))
                page_size = st.selectbox("Rows per page", [10, 25, 50], key="rec_page_size")
                page_count = max(1, (len(table_df) + page_size - 1) // page_size)
                current_page = st.number_input(
                    "Page", min_value=1, max_value=page_count,
                    value=min(int(st.session_state.get("rec_page", 1)), page_count),
                    step=1, key="rec_page",
                )
                start_row = (int(current_page) - 1) * page_size
                show_table(table_df.iloc[start_row:start_row + page_size], "recommendation_table")

    st.caption(
        "Recommendations are based on historical performance in the SocialPulse dataset. "
        "They represent observed content patterns and are not guaranteed future outcomes."
    )

st.markdown("---")
st.caption("Social Sense · Data-driven engagement intelligence")
