from tickersense.rag.news import get_news


def test_get_news_returns_articles_with_titles():
    articles = get_news("AAPL", limit=5)
    assert len(articles) > 0
    for article in articles:
        assert article["title"]
