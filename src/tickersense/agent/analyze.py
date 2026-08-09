from langchain_ollama import ChatOllama

from tickersense.agent.prompts import ANALYSIS_PROMPT, format_news, format_price
from tickersense.config import OLLAMA_BASE_URL, OLLAMA_MODEL

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
            # Generation is the dominant cost (~3 tokens/sec on CPU), so the
            # output length cap is really a latency cap. The prompt asks for
            # 2-3 sentences plus a sentiment line, which fits under this.
            num_predict=150,
            # Keep the model resident between calls. Ollama unloads after 5
            # minutes by default, and a cold reload costs ~7s.
            keep_alive="30m",
        )
    return _llm


def analyze(ticker: str, price_data: dict, news: list[dict]) -> str:
    """Ask the local LLM for a sentiment summary grounded in price + news."""
    chain = ANALYSIS_PROMPT | _get_llm()
    response = chain.invoke(
        {
            "ticker": ticker,
            "price_summary": format_price(price_data),
            "news_summary": format_news(news),
        }
    )
    return response.content
