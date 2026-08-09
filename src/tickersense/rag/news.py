import yfinance as yf


def get_news(ticker: str, limit: int = 10) -> list[dict]:
    """Fetch recent news for a ticker via yfinance.

    Each yfinance news item nests the useful fields under "content".
    """
    stock = yf.Ticker(ticker)
    raw_items = stock.news or []

    articles = []
    for item in raw_items[:limit]:
        content = item.get("content", {})
        title = content.get("title")
        if not title:
            continue

        articles.append(
            {
                "title": title,
                "summary": content.get("summary", ""),
                "publisher": content.get("provider", {}).get("displayName", ""),
                "link": content.get("canonicalUrl", {}).get("url", ""),
                "published_at": content.get("pubDate", ""),
            }
        )

    return articles
