import streamlit as st
import feedparser
from transformers import pipeline
import torch
import pandas as pd
import os
os.environ["TRANSFORMERS_CACHE"] = "/tmp/transformers_cache"

# Initialize the sentiment analysis pipeline
@st.cache_resource(show_spinner=False)
def load_pipeline():
    return pipeline("text-classification", model="ProsusAI/finbert")

pipe = load_pipeline()

# Define a function to fetch and analyze news
def fetch_news(ticker: str, keyword: str):
    rss_url = f'https://finance.yahoo.com/rss/headline?s={ticker}'
    feed = feedparser.parse(rss_url)

    # Data storage for articles and analysis results
    articles = []
    total_score = 0
    num_articles = 0

    for entry in feed.entries:
        # Check if entry has a summary and filter by keyword
        summary = entry.get('summary', '')
        if keyword.lower() not in summary.lower():
            continue

        sentiment = pipe(summary)[0]

        # Collect article data
        articles.append({
            "Title": entry.get('title', 'N/A'),
            "Link": entry.get('link', 'N/A'),
            "Published": entry.get('published', 'N/A'),
            "Summary": summary,
            "Sentiment": sentiment["label"],
            "Score": sentiment["score"]
        })

        # Aggregate sentiment score
        if sentiment['label'] == 'positive':
            total_score += sentiment['score']
            num_articles += 1
        elif sentiment['label'] == 'negative':
            total_score -= sentiment['score']
            num_articles += 1

    overall_sentiment = "Neutral"
    final_score = 0
    if num_articles > 0:
        final_score = total_score / num_articles
        if total_score >= 0.15:
            overall_sentiment = "Positive"
        elif total_score <= -0.15:
            overall_sentiment = "Negative"

    return articles, overall_sentiment, final_score

# Sidebar inputs for interactivity
st.sidebar.title("News Sentiment Analyzer")
ticker = st.sidebar.text_input("Ticker Symbol", value="META")
keyword = st.sidebar.text_input("Keyword to Search in Article Summary", value="meta")

if st.sidebar.button("Fetch and Analyze News"):
    with st.spinner("Fetching news and running sentiment analysis..."):
        articles, overall_sentiment, final_score = fetch_news(ticker, keyword)

    st.header(f"News Analysis for {ticker.upper()}")
    
    # Display overall sentiment
    st.subheader(f"Overall Sentiment: {overall_sentiment} ({final_score:.2f})")
    
    # Display articles in a table format
    if articles:
        df = pd.DataFrame(articles)
        st.dataframe(df)
        
        # Option to view details for each article by expanding sections
        for article in articles:
            with st.expander(article["Title"]):
                st.markdown(f"[Read Article]({article['Link']})")
                st.write(f"**Published:** {article['Published']}")
                st.write(f"**Summary:** {article['Summary']}")
                st.write(f"**Sentiment:** {article['Sentiment']}  (Score: {article['Score']:.2f})")
    else:
        st.warning("No articles matched the criteria.")

# Future Enhancement Section (for Historical Data and Trend Analysis)
st.sidebar.markdown("---")
st.sidebar.info(
    "Future Enhancements:\n"
    "- Incorporate historical data for trend comparisons.\n"
    "- Compare industry-specific news trends.\n"
    "- Enhance interactive filtering and visualization options."
)
