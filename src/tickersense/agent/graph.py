from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from tickersense.agent.analyze import analyze
from tickersense.rag.embed import index_news, retrieve_relevant_news
from tickersense.rag.news import get_news
from tickersense.tools.price import get_price


class AgentState(TypedDict):
    ticker: str
    price_data: Optional[dict]
    news: Optional[list[dict]]
    analysis: Optional[str]


def fetch_price_node(state: AgentState) -> dict:
    return {"price_data": get_price(state["ticker"])}


def retrieve_news_node(state: AgentState) -> dict:
    ticker = state["ticker"]
    articles = get_news(ticker)
    index_news(ticker, articles)

    relevant = retrieve_relevant_news(
        ticker, query=f"news affecting {ticker} stock price", top_k=3
    )
    return {"news": relevant}


def analyze_node(state: AgentState) -> dict:
    summary = analyze(state["ticker"], state["price_data"], state["news"])
    return {"analysis": summary}


def _base_graph() -> StateGraph:
    """The shared front half: price + news retrieval, no LLM."""
    graph = StateGraph(AgentState)
    graph.add_node("fetch_price", fetch_price_node)
    graph.add_node("retrieve_news", retrieve_news_node)
    graph.set_entry_point("fetch_price")
    graph.add_edge("fetch_price", "retrieve_news")
    return graph


def build_snapshot_graph():
    """fetch_price -> retrieve_news -> END.

    Returns grounded data without calling the LLM, so it finishes in seconds.
    Intended for callers that can do their own reasoning over the retrieved
    news — an MCP client like Claude Desktop is itself an LLM.
    """
    graph = _base_graph()
    graph.add_edge("retrieve_news", END)
    return graph.compile()


def build_analysis_graph():
    """fetch_price -> retrieve_news -> analyze -> END.

    The fully self-contained pipeline: the local LLM writes the summary, so
    this runs offline with no external model. Slower — the analyze step is
    dominated by local inference.
    """
    graph = _base_graph()
    graph.add_node("analyze", analyze_node)
    graph.add_edge("retrieve_news", "analyze")
    graph.add_edge("analyze", END)
    return graph.compile()
