# Social Sense — Data-Driven Social Media Engagement Intelligence System

Social Sense is a Streamlit-based dashboard for exploring social media engagement, post performance, virality metrics, audience insights, and historical content recommendations. It connects to an existing FastAPI backend to retrieve and analyze available data.

## Features

### 1. Home
- Social Sense branding and dashboard introduction.
- Performance overview using data returned by the backend.
- **Analyze a Post** button that navigates to the Social Media Post Analyzer.
- Quick overview of the available analytics pages.

### 2. Social Media Post Analyzer
- Enter a supported social media post URL.
- Submit the URL to the existing analysis API.
- View available post information, including platform, title, and engagement metrics.
- Display views, likes, comments, shares, engagement rate, and virality information when returned by the API.
- Handle invalid input and API errors.
- Inspect the complete API response for additional details.

### 3. Virality Calculator
- Calculate basic engagement totals from views, likes, comments, and shares.
- Display engagement per view when views are greater than zero.
- Explore historical top-performing posts returned by the backend.
- Search posts by hashtag or post ID.
- Filter by platform and content type when those fields are available.
- Sort and visualize posts using available virality or engagement metrics.

### 4. Audience Insights
- Explore audience sentiment and engagement insights using available backend data.
- Display data returned by the configured API.
- Show appropriate messages when records or required fields are unavailable.

### 5. Content Recommendations
- Explore historical content patterns and recommendations.
- Review available virality and engagement metrics.
- Search, sort, and paginate recommendation records when supported by the returned data.
- Use historical performance to inform content strategy.

Recommendations describe observed patterns and do not guarantee future performance.

## Technology Stack

- **Python** — application logic
- **Streamlit** — interactive dashboard and navigation
- **Pandas** — data processing and tabular views
- **Plotly** — interactive charts
- **Requests** — communication with the backend API
- **FastAPI** — backend services and analytics endpoints

## Project Structure

```text
Data_Driven_Social_Engagement/
├── app.py
├── requirements.txt
├── social_sense_icon.jpg
├── README.md
└── .venv/                 # Local virtual environment, not committed
```

Other backend files and datasets may exist in the full project repository.

## Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- Git
- A running FastAPI backend
- The backend's required datasets and configuration

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Shruti392301/Data_Driven_Social_Engagement.git
cd Data_Driven_Social_Engagement
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If the virtual environment already exists, activate it instead of creating it again.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Configuration

The dashboard uses the `SOCIALPULSE_API_URL` environment variable to locate the FastAPI backend.

By default, the API URL is:

```text
http://localhost:8000
```

To configure a different backend URL in Windows PowerShell:

```powershell
$env:SOCIALPULSE_API_URL = "http://localhost:8000"
```

Replace the URL with the actual address of your running backend when necessary.

## Running the Application

### 1. Start the FastAPI backend

From the backend directory, use the startup command specified by your project's FastAPI setup. For example, if the backend entry point is `main.py` and it exposes `app`:

```bash
uvicorn main:app --reload --port 8000
```

### 2. Start the Streamlit dashboard

Open another terminal in the project directory, activate the virtual environment, and run:

```bash
streamlit run app.py
```

Streamlit will display a local URL

## Git Workflow

To save and publish local changes:

```bash
git status
git add .
git commit -m "Any message to Commit"
git push origin main
```

## License

No license has been specified for this project yet.