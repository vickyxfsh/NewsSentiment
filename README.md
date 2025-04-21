# Sentiment Dashboard Streamlit App

Front‑desk bankers need to deliver fast, data-driven news updates—but manually scanning headlines takes time and can miss critical signals. Our Streamlit app streamlines that process. It automatically:

1. **Pulls the latest headlines** for any stock ticker from [Yahoo](https://finance.yahoo.com/)
2. **Runs FinBERT sentiment analysis** to classify each article as positive, neutral, or negative 
3. **Displays results in a clear, interactive dashboard** so you can:
   - Drill down on a single stock’s news sentiment  
   - Compare sentiment trends across sectors at a glance  

With just a few clicks, you’ll spot emerging trends, market mood and share insights.

---

## Table of Contents

- [Demo](#demo)
- [Method](#method)  
- [Features](#features)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Code Structure](#code-structure)  
- [Future Enhancements](#future-enhancements)

---

## Demo

[▶️ Watch the demo (MOV file)](https://www.dropbox.com/scl/fi/urc8244e2dhj2cddu56et/demo.mp4?rlkey=altjpmc0vli2ntuqhjrqs5fs3&st=385mj0j0&dl=0)

## Method

[FinBERT](https://huggingface.co/ProsusAI/finbert) is built by further training BERT on a large financial corpus, enabling it to understand sector jargon and deliver reliable sentiment classifications for financial news.


## Features

- **News Sentiment Analyzer**: Filter articles by keyword and view per‑article sentiment (Positive/Neutral/Negative) with summary and publication date.  
- **Industry Trend Analysis**: Check average sentiment scores for leading companies across Tech, Commodity Market, FMCG, Medical, and New Energy sectors.  
- **Interactive UI**: Sidebar navigation, input controls, tables, and expanders for detailed views.  
- **Performance**: Caches the FinBERT pipeline using `@st.cache_resource` to speed up repeated runs.  

---

## Configuration

The app requires a Hugging Face token to access the FinBERT model:

- **Option 1: Streamlit secrets**

  1. Create a file at `.streamlit/secrets.toml`.  
  2. Add your token:

     ```toml
     [secrets]
     HF_TOKEN = "your_huggingface_token_here"
     ```

- **Option 2: Environment variable**

  ```bash
  export HF_TOKEN="your_huggingface_token_here"
  ```
---

## Usage

Run the Streamlit app locally:

```bash
streamlit run app.py
```

1. Open the provided local URL (e.g., `http://localhost:8501`).

2. Use the sidebar to navigate between pages:

   - **News Sentiment Analyzer**: Enter a ticker and keyword, then click **Fetch News Sentiment**.
   - **Industry Trend Analysis**: Select an industry (or _All_) and click **Check Industry Trends**.

3. View sentiment tables and expand for details.

---

## Code Structure

- `app.py`: Main Streamlit application code.  
- `requirements.txt`: List of Python dependencies.  
- `.streamlit/secrets.toml` (optional): Stores the `HF_TOKEN` for Hugging Face.  

---

## Future Enhancements

- Historical sentiment trends with time‑series charts.  
- Custom date range and keyword filtering.  
- Interactive visualizations (bar/line charts).
- Support more industries and companies.



