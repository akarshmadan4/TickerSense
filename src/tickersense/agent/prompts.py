from langchain_core.prompts import ChatPromptTemplate

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a financial analysis assistant. Summarize the stock's "
            "current situation using ONLY the price data and news provided "
            "below — do not invent facts or use outside knowledge. If the "
            "news doesn't clearly point in a direction, say so explicitly. "
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
        f"Current price: {price_data['current_price']} {price_data['currency']}\n"
        f"Previous close: {price_data['previous_close']}\n"
        f"Day range: {price_data['day_low']} - {price_data['day_high']}"
    )


def format_news(news: list[dict]) -> str:
    if not news:
        return "No recent news available."
    return "\n".join(f"- {article['text']} (source: {article['publisher']})" for article in news)
