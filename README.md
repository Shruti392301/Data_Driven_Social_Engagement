# 📊 Data-Driven Social Engagement Dashboard

A Python-based data analytics and machine learning project that analyzes social media performance, engagement, virality, audience sentiment, content patterns, and future trends through an interactive Streamlit dashboard.

## 🎯 Objectives

- Analyze social media content performance
- Calculate engagement and virality metrics
- Compare platforms, content types, hashtags, and regions
- Analyze audience sentiment from comments
- Apply machine learning and statistical analysis
- Recommend high-performing content combinations
- Forecast future virality trends
- Build an interactive Streamlit dashboard

## 📊 Datasets

### Viral Social Media Trends
Contains approximately 5,000 posts with:

- Platform
- Content Type
- Hashtag
- Region
- Views
- Likes
- Shares
- Comments
- Engagement Level
- Post Date

### Social Media Comments
Contains social media comments with sentiment categories:

- `1` → Positive
- `0` → Neutral
- `-1` → Negative

After cleaning, approximately **36,793 unique comments** are used for analysis.

## 🔍 Project Modules

### 1. Data Cleaning
- Missing value handling
- Duplicate removal
- Date conversion
- Data validation
- Anomaly detection

### 2. Engagement & Virality Analysis

**Engagement Rate:**

```text
(Likes + Shares + Comments) / Views × 100
````

**Virality Score:**

```text
[0.60 × Shares/Views]
+ [0.20 × Comments/Views]
+ [0.20 × Likes/Views]
```

### 3. Performance Analysis

Analysis across:

* Platforms
* Content Types
* Hashtags
* Regions
* Monthly trends

### 4. Sentiment Analysis

Uses NLP techniques including:

* NLTK
* TextBlob
* Text preprocessing
* Stopword removal
* Lemmatization

### 5. Machine Learning

Models used:

* Logistic Regression
* Random Forest

Evaluation includes:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix

### 6. Statistical Analysis

* T-Test
* ANOVA
* Correlation Analysis

### 7. Recommendation System

Identifies content combinations based on historical:

* Virality
* Engagement
* Shares
* Platform
* Hashtag
* Content Type

### 8. Trend Forecasting

Uses **Holt Exponential Smoothing** to forecast future monthly virality.

### 9. Streamlit Dashboard

The dashboard provides:

* KPI cards
* Platform analysis
* Content analysis
* Hashtag analysis
* Regional analysis
* Sentiment analysis
* Top viral posts
* Monthly trends
* Future virality forecast
* Interactive filters

## 🛠️ Tech Stack

**Language:** Python 3.12

**Libraries:**

* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn
* NLTK
* TextBlob
* SciPy
* Statsmodels
* Streamlit

**Tools:**

* VS Code
* Jupyter Notebook
* Git
* GitHub

## 📁 Project Structure

```text
Data_Driven_Social_Engagement/
│
├── app.py
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
├── outputs/
│   ├── dashboard/
│   ├── forecasting/
│   ├── ml/
│   ├── recommendations/
│   ├── sentiment/
│   └── statistics/
├── dashboard/
├── docs/
├── requirements.txt
└── README.md
```

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd Data_Driven_Social_Engagement
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the dashboard

```bash
streamlit run app.py
```

## ⚠️ Limitations

* Dataset is static and does not represent live social media data.
* Some records contain unusually high interaction-to-view ratios.
* Virality Score is a project-defined metric.
* Sentiment analysis uses rule-based TextBlob polarity.
* Forecast accuracy depends on historical data patterns.

## 🚀 Future Scope

* Live social media API integration
* Advanced transformer-based sentiment analysis
* Improved virality prediction
* Advanced recommendation models
* Database integration
* Real-time dashboard
* Advanced forecasting models

## 👩‍💻 Author

**Shruti Gaikwad**
B.Tech – Artificial Intelligence and Data Science
PVG's College of Engineering and Technology

---


