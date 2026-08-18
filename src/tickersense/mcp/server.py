from mcp.server import MCPServer

from tickersense.agent.graph import build_analysis_graph, build_snapshot_graph
from tickersense.rag.embed import warm_up
from tickersense.tools.price import format_amount

mcp = MCPServer("TickerSense")

# Built once at import time — LangGraph's compiled graphs are stateless and
# reusable across calls, so there's no reason to rebuild them per request.
_snapshot_agent = build_snapshot_graph()
_analysis_agent = build_analysis_graph()


def _format_price(ticker: str, price: dict) -> str:
    return (
        f"Ticker: {ticker}\n"
        f"Price: {format_amount(price['current_price'])} {price['currency']} "
        f"(prev close {format_amount(price['previous_close'])}, "
        f"day range {format_amount(price['day_low'])}-{format_amount(price['day_high'])})"
    )


@mcp.tool()
def get_stock_snapshot(ticker: str) -> str:
    """Get a live price and the most relevant recent news for a stock.

    Returns the retrieved data without interpreting it, so it responds in a
    few seconds. Use this when you want to reason about the news yourself.

    Works for both US tickers (e.g. AAPL) and Indian tickers
    (e.g. RELIANCE.NS on NSE, TCS.BO on BSE).
    """
    result = _snapshot_agent.invoke({"ticker": ticker})

    lines = [_format_price(ticker, result["price_data"]), "", "Relevant recent news:"]
    for article in result["news"]:
        lines.append(f"- {article['title']} ({article['publisher']})")
        lines.append(f"  {article['text']}")
    return "\n".join(lines)


@mcp.tool()
def get_stock_analysis(ticker: str) -> str:
    """Get a price snapshot plus a written sentiment analysis of a stock.

    Runs the full local pipeline, including a locally-hosted LLM that writes
    the summary. Slower than get_stock_snapshot — often 60 seconds or more —
    so prefer the snapshot tool unless you specifically want this server's own
    written analysis.

    Works for both US tickers (e.g. AAPL) and Indian tickers
    (e.g. RELIANCE.NS on NSE, TCS.BO on BSE).
    """
    result = _analysis_agent.invoke({"ticker": ticker})

    lines = [
        _format_price(ticker, result["price_data"]),
        "",
        "Analysis:",
        result["analysis"],
    ]
    return "\n".join(lines)


def main() -> None:
    # Load the embedding model before serving. It costs ~10s on first use, and
    # paying it at startup keeps that out of the first tool call, which has to
    # fit inside the client's request timeout.
    warm_up()
    mcp.run()


if __name__ == "__main__":
    main()
