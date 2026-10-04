# 📊 SocialPulse

### A Data-Driven Social Media Engagement Intelligence System

**SocialPulse** is a data-driven social media analytics platform that analyzes content performance, engagement, virality, audience sentiment, trends, and future virality patterns.

The system combines **historical social media datasets, machine learning, NLP, statistical analysis, forecasting, and real-time social media post analysis** to provide actionable insights through an interactive dashboard.

## 🎯 Objectives

* Analyze social media content performance
* Calculate engagement and virality metrics
* Compare platforms, content types, hashtags, and regions
* Analyze audience sentiment from comments
* Apply machine learning and statistical techniques
* Recommend high-performing content combinations
* Forecast future virality trends
* Analyze individual social media posts using their URLs
* Provide an interactive web-based analytics dashboard

## 📊 Datasets

### Viral Social Media Trends

Approximately **5,000 social media posts** containing:

* Platform
* Content Type
* Hashtag
* Region
* Views
* Likes
* Shares
* Comments
* Engagement Level
* Post Date

### Social Media Comments

A sentiment dataset containing approximately **36,793 cleaned comments** categorized as:

* `1` → Positive
* `0` → Neutral
* `-1` → Negative

## 🔍 Core Modules

### 1. Data Cleaning & Preprocessing

* Missing value handling
* Duplicate removal
* Date conversion
* Data validation
* Anomaly detection
* Feature engineering

### 2. Engagement & Virality Analysis

**Engagement Rate:**

```text
(Likes + Shares + Comments) / Views × 100
```

**Virality Score:**

```text
0.60 × Shares/Views
+ 0.20 × Comments/Views
+ 0.20 × Likes/Views
```

### 3. Performance Analysis

Analyzes performance across:

* Platforms
* Content Types
* Hashtags
* Regions
* Monthly trends

### 4. Audience Sentiment Analysis

Uses NLP techniques including:

* NLTK
* TextBlob
* Text preprocessing
* Stopword removal
* Lemmatization

### 5. Machine Learning

Machine learning models are used for engagement and virality-related analysis.

Models include:

* Logistic Regression
* Random Forest

Evaluation metrics include:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix

### 6. Statistical Analysis

Statistical techniques include:

* T-Test
* ANOVA
* Correlation Analysis

### 7. Recommendation System

Identifies potentially high-performing content combinations using historical patterns involving:

* Platform
* Hashtag
* Content Type
* Engagement
* Shares
* Virality

### 8. Trend Forecasting

Uses **Holt Exponential Smoothing** to forecast future monthly virality trends based on historical data.

### 9. Real-Time Post Analyzer

SocialPulse can analyze individual social media posts through their URLs.

The Post Analyzer:

* Detects the social media platform
* Retrieves available post information
* Fetches current engagement metrics
* Calculates engagement and virality metrics
* Classifies post performance
* Compares the post with historical SocialPulse data

Currently supports real-time analysis for supported **YouTube and Instagram** posts.

## 🖥️ Dashboard

The Streamlit dashboard provides:

* 📊 Overview analytics
* 📈 Platform performance
* 🔥 Virality Explorer
* 👥 Audience sentiment insights
* 💡 Content recommendations
* 📅 Trend forecasting
* 🔗 Real-time Post Analyzer
* KPI cards
* Interactive charts
* Platform and content comparisons

## 🛠️ Tech Stack

### Programming

* Python 3.12

### Data & Machine Learning

* Pandas
* NumPy
* Scikit-learn
* SciPy
* Statsmodels

### NLP

* NLTK
* TextBlob
* spaCy

### Visualization

* Plotly
* Matplotlib

### Web Application

* Streamlit
* FastAPI
* Uvicorn

### APIs & Data Extraction

* YouTube Data API
* Instagram API
* Requests
* BeautifulSoup

### Development Tools

* VS Code
* Jupyter Notebook
* Git
* GitHub

## 📁 Project Structure

```text
Data_Driven_Social_Engagement/
│
├── app.py
├── backend/
│   ├── main.py
│   └── api/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
├── outputs/
│   ├── dashboard/
│   ├── forecasting/
│   ├── ml/
│   ├── recommendations/
│   ├── sentiment/
│   └── statistics/
│
├── docs/
├── requirements.txt
└── README.md
```

## ▶️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Shruti392301/Data_Driven_Social_Engagement.git

cd Data_Driven_Social_Engagement
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Start the FastAPI backend

```bash
python -m uvicorn backend.main:app --reload
```

### 6. Start the Streamlit dashboard

Open another terminal and run:

```bash
streamlit run app.py
```

The dashboard will then be available locally through the Streamlit URL.

## 🌐 Deployment

SocialPulse is deployed using:

* **Streamlit** — Frontend Dashboard
* **Render** — FastAPI Backend

The deployed architecture separates the interactive dashboard from the API backend, allowing the Post Analyzer to retrieve real-time social media data while the other modules use historical datasets and trained models.

## ⚠️ Limitations

* Historical analytics depend on the available datasets.
* Social media API access depends on platform availability and API permissions.
* Some social media posts may not be publicly accessible through APIs.
* Virality Score is a project-defined metric.
* Forecast accuracy depends on historical patterns.
* Real-time metrics may change after analysis because social media engagement is dynamic.

## 🚀 Future Scope

* Transformer-based sentiment analysis
* Advanced deep learning models for virality prediction
* Personalized recommendation models
* Database integration for scalable storage
* Real-time monitoring of multiple posts
* Advanced time-series forecasting
* Additional social media platform integrations
* Automated content strategy generation

## 👩‍💻 Author

**Shruti Gaikwad**

B.Tech – Artificial Intelligence and Data Science
PVG's College of Engineering and Technology
