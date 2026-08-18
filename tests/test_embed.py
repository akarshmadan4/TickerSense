from datetime import datetime, timedelta, timezone

from tickersense.rag.embed import index_news, retrieve_relevant_news


def _iso_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

SAMPLE_ARTICLES = [
    {
        "title": "Apple unveils new iPhone with AI features",
        "summary": "The device includes on-device machine learning chips.",
        "publisher": "TestWire",
        "link": "https://example.com/apple-ai-phone",
    },
    {
        "title": "Apple faces supply chain delays in Asia",
        "summary": "Component shortages could push shipments into next quarter.",
        "publisher": "TestWire",
        "link": "https://example.com/apple-supply-chain",
    },
]


def test_retrieve_relevant_news_ranks_by_similarity():
    index_news("TESTAAPL", SAMPLE_ARTICLES)

    results = retrieve_relevant_news("TESTAAPL", query="AI chip features", top_k=1)

    assert len(results) == 1
    assert "AI" in results[0]["title"]


def test_retrieve_excludes_articles_outside_the_recency_window():
    """An older, more on-topic article must lose to the recency filter.

    The stale article is written to match the query more closely than the
    fresh one, so a pass here means the window is doing the work rather than
    similarity happening to agree.
    """
    ticker = "TESTRECENCY"
    index_news(
        ticker,
        [
            {
                "title": "Quarterly earnings beat expectations on strong margins",
                "summary": "Earnings, margins and revenue all ahead of guidance.",
                "publisher": "TestWire",
                "link": "https://example.com/stale-earnings",
                "published_at": _iso_days_ago(60),
            },
            {
                "title": "Factory reopens after maintenance shutdown",
                "summary": "Production resumes at the northern plant.",
                "publisher": "TestWire",
                "link": "https://example.com/fresh-factory",
                "published_at": _iso_days_ago(1),
            },
        ],
    )

    results = retrieve_relevant_news(
        ticker, query="quarterly earnings and margins", top_k=1, max_age_days=14
    )

    assert len(results) == 1
    assert results[0]["link"] == "https://example.com/fresh-factory"


def test_retrieve_falls_back_when_nothing_is_recent_enough():
    """A ticker whose news has all aged out should still return something."""
    ticker = "TESTALLSTALE"
    index_news(
        ticker,
        [
            {
                "title": "Long-past product announcement",
                "summary": "A launch event from a previous quarter.",
                "publisher": "TestWire",
                "link": "https://example.com/all-stale",
                "published_at": _iso_days_ago(90),
            }
        ],
    )

    results = retrieve_relevant_news(
        ticker, query="product launch", top_k=1, max_age_days=14
    )

    assert len(results) == 1
    assert results[0]["link"] == "https://example.com/all-stale"
