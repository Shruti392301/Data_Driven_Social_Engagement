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

**Note:** The basic arithmetic displayed by the calculator is not a replacement for the project's backend virality-scoring algorithm.

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

If the requirements file is incomplete, the dashboard directly imports Streamlit, Requests, Pandas, and Plotly. Install any missing packages before running the app.

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

The backend must expose the endpoints expected by the dashboard. Available features depend on the backend implementation and the data it returns.

## Running the Application

### 1. Start the FastAPI backend

From the backend directory, use the startup command specified by your project's FastAPI setup. For example, if the backend entry point is `main.py` and it exposes `app`:

```bash
uvicorn main:app --reload --port 8000
```

Adjust the module and application names to match your backend files.

### 2. Start the Streamlit dashboard

Open another terminal in the project directory, activate the virtual environment, and run:

```bash
streamlit run app.py
```

Streamlit will display a local URL, typically:

```text
http://localhost:8501
```

Open that URL in your browser.

## API Integration

The dashboard communicates with the configured FastAPI service.

| Endpoint | Purpose |
|---|---|
| `GET /api/summary` | Retrieve the Home page performance summary |
| `POST /api/analyze-post` | Analyze a submitted social media post URL |
| `GET /api/top-posts` | Retrieve records for the Top Viral Posts section |

Additional API endpoints are used by the Audience Insights and Content Recommendations pages. Their exact paths and response schemas depend on the backend implementation.

The dashboard expects JSON responses and reports API connection errors, HTTP errors, and unavailable records where handled by the interface.

## Error Handling and Data Integrity

- API requests use timeouts.
- HTTP and connection errors are handled in the interface.
- Nested API responses are inspected without assuming every field is a scalar.
- Missing data is not intentionally replaced with fabricated post records.
- Charts and tables depend on the fields returned by the backend.
- Backend calculations remain the source of truth for backend-generated analytics.

## Git Workflow

To save and publish local changes:

```bash
git status
git add README.md
git commit -m "Update project README"
git push origin main
```

To include other intended changes, stage those files separately or use `git add .` after reviewing `git status`.

## Troubleshooting

**The dashboard cannot connect to the API**
- Confirm that the FastAPI backend is running.
- Verify `SOCIALPULSE_API_URL`.
- Check that the expected endpoint exists and returns JSON.

**A chart or table has no records**
- Confirm that the backend returns records in a supported response format.
- Check that the required columns exist in the response.
- Verify that the backend datasets are available.

**A package is missing**
- Activate the virtual environment.
- Run `python -m pip install -r requirements.txt`.

**The Home page navigation does not switch pages**
- Confirm that the button updates `st.session_state.socialpulse_page`.
- Ensure the destination matches the page name used by the sidebar navigation.

## Future Improvements

- Add automated tests for navigation and API response handling.
- Improve API health and connection-status reporting.
- Add additional filters and export options where supported by the data.
- Expand analytics while preserving the existing backend logic.

## License

Add the license applicable to this project before distributing or reusing it publicly.
