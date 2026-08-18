from langchain_core.prompts import ChatPromptTemplate

from tickersense.rag.news import format_published
from tickersense.tools.price import format_amount

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a financial analysis assistant. Summarize the stock's "
            "current situation using ONLY the price data and news provided "
            "below — do not invent facts or use outside knowledge. If the "
            "news doesn't clearly point in a direction, say so explicitly. "
            "An article may mention a different company; ignore any article "
            "that is not about the ticker in question, and never attribute "
            "another company's news to this one. If none of the articles are "
            "about it, say the available news does not cover this company "
            "rather than drawing conclusions from unrelated stories. "
            "Keep the summary to 2-3 short sentences, then end with a single line: "
            "'Sentiment: Positive' | 'Sentiment: Negative' | 'Sentiment: Neutral'.",
        ),
        (
            "human",
            "Ticker: {ticker}\n\nPrice data:\n{price_summary}\n\nRecent news:\n{news_summary}",
        ),
    ]
)


def format_price(price_data: dict) -> str:
    return (
        f"Current price: {format_amount(price_data['current_price'])} {price_data['currency']}\n"
        f"Previous close: {format_amount(price_data['previous_close'])}\n"
        f"Day range: {format_amount(price_data['day_low'])} - {format_amount(price_data['day_high'])}"
    )


def format_news(news: list[dict]) -> str:
    if not news:
        return "No recent news available."

    lines = []
    for article in news:
        published = format_published(article.get("published_ts"))
        dateline = f", {published}" if published else ""
        lines.append(f"- {article['text']} (source: {article['publisher']}{dateline})")
    return "\n".join(lines)
