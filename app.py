import streamlit as st
import feedparser
from transformers import pipeline
import pandas as pd
import os
from datetime import datetime
from huggingface_hub import login

# ——— Hugging Face token setup ———
def get_hf_token():
    return st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

token = get_hf_token()
if not token:
    st.error("HF_TOKEN not found.")
    st.stop()

login(token=token)

# ——— Load sentiment pipeline ———
@st.cache_resource(show_spinner=False)
def load_pipeline():
    return pipeline(
        task="text-classification",
        model="ProsusAI/finbert",
    )

pipe = load_pipeline()

# ——— Fetch & analyze news ———
def fetch_news(ticker: str, keyword: str):
    rss_url = f'https://finance.yahoo.com/rss/headline?s={ticker}'
    feed = feedparser.parse(rss_url)

    total_score = 0.0
    count = 0
    articles = []

    for entry in feed.entries:
        summary = entry.get('summary', '')
        if keyword.lower() not in summary.lower():
            continue

        sentiment = pipe(summary)[0]
        label = sentiment['label'].lower()
        score = sentiment['score']

        # parse & reformat published date
        pub = entry.get('published', '')
        try:
            dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z")
            pub_fmt = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pub_fmt = pub

        articles.append({
            "Title": entry.get('title', ''),
            "Link": entry.get('link', ''),
            "Published": pub_fmt,
            "Summary": summary,
            "Sentiment": label.title(),
            "Score": round(score, 2)
        })

        # accumulate score
        total_score += (score if label == 'positive' else -score)
        count += 1

    # overall sentiment
    if count == 0:
        return articles, 'Neutral', 0.0

    avg_score = total_score / count
    if avg_score >= 0.15:
        overall = 'Positive'
    elif avg_score <= -0.15:
        overall = 'Negative'
    else:
        overall = 'Neutral'

    return articles, overall, avg_score

# ——— Sidebar & navigation ———
st.sidebar.title("Sentiment Dashboard")
page = st.sidebar.radio("Navigate to", ["📊 News Sentiment Analyzer", "📈 Industry Trend Analysis"])

# ——— Page 1: News Sentiment Analyzer ———
if page == "📊 News Sentiment Analyzer":
    st.title("📊 News Sentiment Analyzer")
    st.info(
        """
        **👋 New here?**  
        1. Enter your **Ticker** (e.g. META)  
        2. Enter a **Keyword** to filter article summaries (e.g. meta, amazon, apple, etc.)  
        3. Click **Fetch News Sentiment**  
        """
    )
    ticker = st.text_input("Ticker Symbol", value="META")
    keyword = st.text_input("Keyword", value="meta")
    if st.button("Fetch News Sentiment"):
        with st.spinner("Analyzing…"):
            articles, overall, avg_score = fetch_news(ticker, keyword)

        st.subheader(f"Overall Sentiment: {overall} ({avg_score:.2f})")

        if articles:
            # Compact table view
            df = pd.DataFrame(articles)
            st.dataframe(df[["Title", "Published", "Sentiment"]])

            # Expanders for full details
            for art in articles:
                with st.expander(f"## **{art['Title']}**"):
                    st.markdown(f"[Read Article]({art['Link']})")
                    st.write(f"**Published:** {art['Published']}")
                    st.write(f"**Summary:** {art['Summary']}")
                    st.write(f"**Sentiment:** {art['Sentiment']} ")
        else:
            st.info("No articles matched your keyword.")

# ——— Page 2: Industry Trend Analysis ———
elif page == "📈 Industry Trend Analysis":
    st.title("📈 Industry Trend Sentiment Analysis (Past 3 days)")

    industries = {
        'Tech': {
            'Apple': 'AAPL', 'Microsoft': 'MSFT', 'Amazon': 'AMZN',
            'Alphabet': 'GOOGL', 'Meta': 'META', 'Nvidia': 'NVDA',
            'Intel': 'INTC', 'Oracle': 'ORCL', 'Adobe': 'ADBE',
            'Salesforce': 'CRM', 'Tesla': 'TSLA'
        },
        'Commodity Market': {
            'Freeport-McMoRan': 'FCX', 'Newmont': 'NEM',
            'Barrick Gold': 'GOLD', 'Vale': 'VALE', 'BHP Group': 'BHP',
            'Teck Resources': 'TECK', 'Nutrien': 'NTR', 'Glencore': 'GLNCY',
            'Anglo American': 'NGLOY', 'Rio Tinto': 'RIO'
        },
        'Fast-moving Consumer Goods (FMCG)': {
            'Procter & Gamble': 'PG', 'Unilever': 'UL', 'Nestlé': 'NSRGY',
            'Coca‑Cola': 'KO', 'PepsiCo': 'PEP', 'Colgate‑Palmolive': 'CL',
            'Mondelez International': 'MDLZ', 'Kimberly‑Clark': 'KMB',
            'Philip Morris International': 'PM', 'Diageo': 'DEO'
        },
        'Medical': {
            'Johnson & Johnson': 'JNJ', 'Pfizer': 'PFE', 'Merck & Co.': 'MRK',
            'AbbVie': 'ABBV', 'Medtronic': 'MDT', 'UnitedHealth Group': 'UNH',
            'Amgen': 'AMGN', 'Gilead Sciences': 'GILD', 'Bristol‑Myers Squibb': 'BMY',
            'Eli Lilly': 'LLY'
        },
        'New Energy': {
            'NextEra Energy': 'NEE', 'Enphase Energy': 'ENPH', 'Plug Power': 'PLUG',
            'First Solar': 'FSLR', 'SolarEdge Technologies': 'SEDG',
            'Bloom Energy': 'BE', 'Brookfield Renewable Partners': 'BEP',
            'ChargePoint Holdings': 'CHPT', 'FuelCell Energy': 'FCEL'
        }
    }

    choice = st.selectbox("Select industry to view", ["All"] + list(industries.keys()))
    if st.button("Check Industry Trends"):
        results = []
        with st.spinner("Analyzing…"):
            sectors = [choice] if choice != "All" else industries.keys()
            for sector in sectors:
                for name, sym in industries[sector].items():
                    _, label, avg_score = fetch_news(sym, name)
                    results.append({
                        "Industry": sector,
                        "Company": name,
                        "Score": round(avg_score, 2),
                        "Sentiment": label
                    })

        df2 = pd.DataFrame(results)
        if df2.empty:
            st.warning("No data for that selection.")
        else:
            # Simple bar chart of average scores
            # chart_data = df2.set_index("Company")["Score"]
            # st.bar_chart(chart_data)

            # Optional: raw numbers
            st.table(df2[["Industry", "Company", "Score", "Sentiment"]])

# ——— Footer ———
st.sidebar.markdown("---")
st.sidebar.markdown("**Problem:** \n Front‑desk bankers must deliver quick, data‑driven updates, but manually scanning news is slow")
st.sidebar.markdown("**Solution:** \n Our Streamlit app automatically collects headlines, runs [FinBERT](https://huggingface.co/ProsusAI/finbert) sentiment analysis, and then displays single‑stock and sector views in a clear dashboard, so bankers can spot trends at a glance and get useful insights.")

st.sidebar.markdown("---")
st.sidebar.info("Future Enhancements: Add historical trend charts and deeper filtering.")
