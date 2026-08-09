import yfinance as yf


def get_price(ticker: str) -> dict:
    """Fetch a current price snapshot for a ticker.

    Works for both US tickers (e.g. AAPL) and Indian tickers
    (e.g. RELIANCE.NS, RELIANCE.BO) — yfinance resolves the
    exchange from the suffix.
    """
    stock = yf.Ticker(ticker)
    info = stock.fast_info

    return {
        "ticker": ticker,
        "current_price": info.get("lastPrice"),
        "previous_close": info.get("previousClose"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "currency": info.get("currency"),
    }
