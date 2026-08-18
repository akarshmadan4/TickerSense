from tickersense.tools.company import get_company_keywords, mentions_company


def test_keywords_include_company_name_and_ticker_root():
    keywords = get_company_keywords("RELIANCE.NS")

    assert "reliance" in keywords


def test_keywords_include_name_when_it_differs_from_the_symbol():
    """AAPL is the case the ticker root alone cannot cover."""
    keywords = get_company_keywords("AAPL")

    assert "apple" in keywords
    assert "aapl" in keywords


def test_mentions_company_matches_whole_words_only():
    keywords = frozenset({"tcs", "tata"})

    assert mentions_company("TCS wins a new contract", keywords)
    assert not mentions_company("The gotchas of deployment", keywords)


def test_mentions_company_is_case_insensitive():
    assert mentions_company("RELIANCE posts results", frozenset({"reliance"}))


def test_unrelated_article_is_rejected():
    """The exact failure that motivated this: Rolls-Royce under RELIANCE.NS."""
    keywords = frozenset({"reliance"})
    article = (
        "Rolls-Royce Stock Hits First New High In 14 Years. "
        "Shares climbed to a record after a jet-engine project announcement."
    )

    assert not mentions_company(article, keywords)


def test_no_keywords_means_no_filtering():
    """An unidentifiable company must not filter everything away."""
    assert mentions_company("anything at all", frozenset())
