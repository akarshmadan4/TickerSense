from tickersense.tools.price import get_price


def test_get_price_us_ticker():
    result = get_price("AAPL")
    assert result["ticker"] == "AAPL"
    assert result["current_price"] > 0


def test_get_price_indian_ticker():
    result = get_price("RELIANCE.NS")
    assert result["ticker"] == "RELIANCE.NS"
    assert result["current_price"] > 0
