import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment(symbol: str) -> dict:
    """
    Fetches the latest news for a symbol and computes NLP sentiment scores.
    """
    ticker = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
    try:
        news_items = yf.Ticker(ticker).news
    except Exception:
        news_items = []
        
    if not news_items:
        return {
            "overall_compound": 0.0,
            "overall_label": "Neutral (No News)",
            "articles": []
        }
        
    analyzer = SentimentIntensityAnalyzer()
    
    articles = []
    total_compound = 0.0
    valid_articles = 0
    
    for item in news_items:
        content = item.get("content", {})
        title = content.get("title", "")
        
        provider = content.get("provider", {})
        publisher = provider.get("displayName", "Unknown Publisher") if isinstance(provider, dict) else provider
        
        link_dict = content.get("clickThroughUrl", content.get("canonicalUrl", {}))
        link = link_dict.get("url", "") if isinstance(link_dict, dict) else link_dict
        
        if not title:
            continue
            
        scores = analyzer.polarity_scores(title)
        comp = scores["compound"]
        
        if comp >= 0.05:
            label = "Bullish"
        elif comp <= -0.05:
            label = "Bearish"
        else:
            label = "Neutral"
            
        articles.append({
            "title": title,
            "publisher": publisher,
            "link": link,
            "compound": comp,
            "label": label
        })
        
        total_compound += comp
        valid_articles += 1
        
    if valid_articles == 0:
        overall = 0.0
    else:
        overall = total_compound / valid_articles
        
    if overall >= 0.05:
        overall_label = "Bullish"
    elif overall <= -0.05:
        overall_label = "Bearish"
    else:
        overall_label = "Neutral"
        
    return {
        "overall_compound": overall,
        "overall_label": overall_label,
        "articles": articles
    }
