import sys

from tickersense.agent.graph import build_analysis_graph
from tickersense.tools.price import format_amount


def main() -> None:
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    agent = build_analysis_graph()
    result = agent.invoke({"ticker": ticker})

    price = result["price_data"]
    print(f"\n=== {ticker} ===")
    print(f"Price: {format_amount(price['current_price'])} {price['currency']} "
          f"(prev close {format_amount(price['previous_close'])})")

    print(f"\nBased on {len(result['news'])} recent articles:")
    for article in result["news"]:
        print(f"  - {article['title']} ({article['publisher']})")

    print(f"\nAnalysis:\n{result['analysis']}\n")


if __name__ == "__main__":
    main()
