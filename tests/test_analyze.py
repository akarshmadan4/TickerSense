from tickersense.agent.analyze import analyze

PRICE_DATA = {
    "current_price": 313.33,
    "previous_close": 312.56,
    "day_high": 314.81,
    "day_low": 310.74,
    "currency": "USD",
}

NEWS = [
    {
        "text": "Apple beats earnings expectations. Revenue up 22% year over year.",
        "publisher": "TestWire",
        "title": "Apple beats earnings expectations",
        "link": "https://example.com/apple-earnings",
    }
]


def test_analyze_returns_nonempty_grounded_summary():
    result = analyze("AAPL", PRICE_DATA, NEWS)
    assert isinstance(result, str)
    assert len(result) > 0
