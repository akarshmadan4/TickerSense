from datetime import datetime, timezone

import yfinance as yf

from tickersense.tools.company import get_company_keywords, mentions_company


def format_published(ts) -> str:
    """Render a stored publish timestamp as YYYY-MM-DD, empty if unknown.

    Shown alongside each article so the age of the evidence is visible — both
    to a reader and to the LLM, which otherwise has no way to know whether a
    headline is from yesterday or last month.
    """
    if not ts:
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def get_news(ticker: str, limit: int = 10) -> list[dict]:
    """Fetch recent news for a ticker via yfinance, keeping only its own news.

    Each yfinance news item nests the useful fields under "content".

    The feed a ticker returns is not restricted to that company, so articles
    that never mention it are dropped here rather than indexed. Filtering at
    ingest keeps the vector store clean, which means the noise can never come
    back through retrieval later.

    There is deliberately no fallback when everything is filtered out. If no
    article mentions the company, then there is no recent news about it, and
    saying so is more useful than analysing somebody else's. This differs from
    the recency filter in embed.py, which does fall back -- an old article
    about the company is still about the company, but a fresh article about a
    different company is worthless here.

    `limit` caps the articles kept, not the articles examined, so a noisy feed
    still yields a full set of relevant ones where they exist.
    """
    stock = yf.Ticker(ticker)
    raw_items = stock.news or []
    keywords = get_company_keywords(ticker)

    articles = []
    for item in raw_items:
        if len(articles) >= limit:
            break

        content = item.get("content", {})
        title = content.get("title")
        if not title:
            continue

        summary = content.get("summary", "")
        if not mentions_company(f"{title} {summary}", keywords):
            continue

        articles.append(
            {
                "title": title,
                "summary": summary,
                "publisher": content.get("provider", {}).get("displayName", ""),
                "link": content.get("canonicalUrl", {}).get("url", ""),
                "published_at": content.get("pubDate", ""),
            }
        )

    return articles
