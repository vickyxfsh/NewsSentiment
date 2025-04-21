from textblob import TextBlob
import nltk
import re
import pandas as pd

# Load the Loughran-McDonald Dictionary
df = pd.read_csv("LM-SA-2020.csv")
print(df.head())

# Each word is mapped to a sentiment score.
# A positive word returns +1, negative returns -1, uncertain may return 0.
LEXICON = {}
for _, row in df.iterrows():
    word = row['word'].strip().lower()  # ensure consistent case
    sentiment = row['sentiment']
    if sentiment == "positive":
        score = 1
    elif sentiment == "negative":
        score = -1
    else:
        score = 0
    LEXICON[word] = score

# Define the main sentiment analysis function that uses both TextBlob and a lexicon-based approach
def find_sentiment(news_story):
    # -- TextBlob-based sentiment analysis --
    news = TextBlob(news_story)
    
    # Extract sentiment from TextBlob
    tb_sentiments = []
    for sentence in news.sentences:
        polarity, subjectivity = sentence.sentiment
        tb_sentiments.append((polarity, subjectivity))
    
    # Compute average polarity and subjectivity from TextBlob results
    if tb_sentiments:
        avg_polarity = sum([p for p, s in tb_sentiments]) / len(tb_sentiments)
        avg_subjectivity = sum([s for p, s in tb_sentiments]) / len(tb_sentiments)
    else:
        avg_polarity = avg_subjectivity = 0

    # -- Lexicon-based sentiment analysis --
    lexicon_score, lexicon_word_count = lexicon_sentiment(news_story)
    # Normalize lexicon score by word count if available
    if lexicon_word_count:
        avg_lexicon_score = lexicon_score / lexicon_word_count
    else:
        avg_lexicon_score = 0

    # Print both analysis results side-by-side
    print("\nFINAL ANALYSIS")
    print("----------------------------------")
    print("\nLexicon-Based Analysis:")
    print(f"  Lexicon Score (average per word): {avg_lexicon_score:.3f} => {interpret_lexicon_score(avg_lexicon_score)}")


# New helper method: Lexicon-based sentiment analysis.
def lexicon_sentiment(text):
    """
    Simple lexicon-based sentiment analysis:
    - Splits text into words using a basic regex (you might want to refine this).
    - Checks each word against the lexicon.
    - Returns the total sentiment score and the number of words matched.
    """
    # Normalize text to lowercase and split into words (removing punctuation)
    words = re.findall(r'\b\w+\b', text.lower())
    total_score = 0
    matched_count = 0
    for word in words:
        if word in LEXICON:
            total_score += LEXICON[word]
            matched_count += 1
    return total_score, matched_count


# A helper to interpret the average lexicon score into a category.
def interpret_lexicon_score(avg_score):
    if avg_score > 0.5:
        return "Bullish sentiment."
    elif avg_score > 0.1:
        return "Slightly bullish sentiment."
    elif avg_score < -0.5:
        return "Bearish sentiment."
    elif avg_score < -0.1:
        return "Slightly bearish sentiment."
    else:
        return "Neutral sentiment."


# Example: Using hard-coded financial news text
if __name__ == "__main__":
    news_text = """With stocks in a steep decline and tariffs inducing recession jitters, investor patience may be tested.
    The notion that the Fed will rush to rescue investors is fading, as Federal Reserve Chair Jerome Powell stated the tariffs are larger than expected.
    
    Despite a robust job report, the outlook remains uncertain, and many fear that a bear market may be on the horizon.
    The potential for recession, combined with aggressive tariffs, has left many investors apprehensive."""
    
    find_sentiment(news_text)
