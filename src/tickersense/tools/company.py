import re
from functools import lru_cache

import yfinance as yf

# Corporate boilerplate that identifies no company in particular.
_STOPWORDS = frozenset(
    {
        "the", "and", "ltd", "limited", "inc", "incorporated", "corp",
        "corporation", "company", "co", "plc", "sa", "nv", "ag", "holdings",
        "holding", "international", "global",
    }
)


@lru_cache(maxsize=128)
def get_company_keywords(ticker: str) -> frozenset[str]:
    """Words that identify this company in a headline.

    yfinance's news feed for a ticker is not restricted to that company. A
    request for RELIANCE.NS returns Rolls-Royce, a Texas op-ed about oil
    prices, and an unrelated small-cap, with no field anywhere in the response
    saying which article is about whom. Matching the company's own name is the
    only signal available, so relevance has to be decided here rather than by
    ranking further downstream.

    Returns the ticker root plus the first distinctive word of the company
    name -- RELIANCE.NS -> {"reliance"}, AAPL -> {"aapl", "apple"} -- because
    headlines use either form.

    This costs one `.info` call per ticker. That is the heavier yfinance
    endpoint deliberately avoided in get_price, and the reversal is deliberate:
    it is paid once per ticker rather than per request, it is cached for the
    life of the process, and it buys correctness rather than convenience.

    Returns an empty set when the name cannot be determined. Callers read that
    as "do not filter" -- failing open, since filtering against a name we
    could not look up would discard every article.
    """
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        return frozenset()

    name = info.get("longName") or info.get("shortName") or info.get("displayName")
    if not name:
        return frozenset()

    keywords = set()

    root = ticker.split(".")[0].strip().lower()
    if len(root) >= 2:
        keywords.add(root)

    # Only the first distinctive word. Later words are usually sector nouns
    # ("Industries", "Consultancy") that would match half the market.
    for word in re.findall(r"[A-Za-z]+", name.lower()):
        if len(word) >= 3 and word not in _STOPWORDS:
            keywords.add(word)
            break

    return frozenset(keywords)


def mentions_company(text: str, keywords: frozenset[str]) -> bool:
    """Whether any identifying word appears in `text` as a whole word.

    Whole-word matching matters: a substring test for "tcs" would hit inside
    unrelated words, and one for "co" would match everything.

    An empty keyword set means the company could not be identified, so this
    returns True rather than rejecting everything.
    """
    if not keywords:
        return True

    lowered = text.lower()
    return any(re.search(rf"\b{re.escape(word)}\b", lowered) for word in keywords)
