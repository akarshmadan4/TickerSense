import yfinance as yf


def format_amount(value) -> str:
    """Render a price for display, to two decimals.

    yfinance returns full float precision (1321.4000244140625), which is noise
    in text meant to be read by a person or an LLM. Rounding happens here
    rather than in get_price so callers doing arithmetic still get the
    unrounded value.

    Missing fields stay readable rather than raising — yfinance omits some
    fields for some tickers.
    """
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


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
