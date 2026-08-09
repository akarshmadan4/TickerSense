from tickersense.rag.embed import index_news, retrieve_relevant_news

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
