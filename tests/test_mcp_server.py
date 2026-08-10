from tickersense.mcp.server import get_stock_analysis, get_stock_snapshot


def test_get_stock_snapshot_returns_price_and_news():
    output = get_stock_snapshot("AAPL")
    assert "Ticker: AAPL" in output
    assert "Price:" in output
    assert "Relevant recent news:" in output


def test_get_stock_analysis_returns_price_and_analysis():
    output = get_stock_analysis("AAPL")
    assert "Ticker: AAPL" in output
    assert "Price:" in output
    assert "Analysis:" in output
