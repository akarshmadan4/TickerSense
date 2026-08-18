from datetime import datetime, timedelta, timezone

import chromadb
from chromadb.utils import embedding_functions

_CHROMA_PATH = "data/chroma"
_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_client = None
_embedding_fn = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=_CHROMA_PATH)
    return _client


def _get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=_EMBEDDING_MODEL
        )
    return _embedding_fn


def warm_up() -> None:
    """Load the embedding model now rather than on first use.

    Callers that care about the latency of their first request (the MCP
    server) can pay this ~10s cost at startup instead.
    """
    _get_embedding_fn()


def _collection_name(ticker: str) -> str:
    return f"news_{ticker.replace('.', '_').lower()}"


def _get_collection(ticker: str):
    return _get_client().get_or_create_collection(
        name=_collection_name(ticker),
        embedding_function=_get_embedding_fn(),
    )


def _published_ts(article: dict) -> int:
    """Epoch seconds for an article's publish time; 0 if it can't be parsed.

    Stored as a number rather than the raw string so ChromaDB can range-filter
    on it. Unparseable dates become 0 so they sort as ancient — an article of
    unknown age is kept out of the recency window rather than passed off as
    fresh.
    """
    raw = article.get("published_at") or ""
    try:
        return int(datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp())
    except (TypeError, ValueError):
        return 0


def index_news(ticker: str, articles: list[dict]) -> None:
    """Embed each new article and store it in the ticker's ChromaDB collection.

    Articles are keyed on their URL. Anything already in the collection is
    skipped rather than re-embedded — embedding is the slow part here, and
    consecutive runs mostly see the same headlines.
    """
    if not articles:
        return

    collection = _get_collection(ticker)
    ids = [a["link"] or f"{ticker}-{i}" for i, a in enumerate(articles)]
    already_indexed = set(collection.get(ids=ids, include=[])["ids"])

    new = [(i, a) for i, a in zip(ids, articles) if i not in already_indexed]
    if not new:
        return

    collection.add(
        ids=[i for i, _ in new],
        documents=[f"{a['title']}. {a['summary']}".strip() for _, a in new],
        metadatas=[
            {
                "title": a["title"],
                "publisher": a["publisher"],
                "link": a["link"],
                "published_ts": _published_ts(a),
            }
            for _, a in new
        ],
    )


def retrieve_relevant_news(
    ticker: str, query: str, top_k: int = 3, max_age_days: int = 14
) -> list[dict]:
    """Return the top_k articles for this ticker most relevant to `query`.

    For news, similarity alone is the wrong ranking. Generic market commentary
    from a month ago scores well against a query about share prices precisely
    because it is about share prices, and it will outrank a company-specific
    story from yesterday. Recency is a relevance signal in its own right, so
    anything older than `max_age_days` is excluded before ranking rather than
    competing on similarity.

    The index is never pruned, so old articles stay on disk; this filters them
    out at query time instead, which keeps the history without letting it
    answer for the present.

    If nothing falls inside the window — a quiet ticker, or a feed that has
    gone stale — it falls back to unfiltered similarity so the tool still
    answers rather than returning nothing.
    """
    collection = _get_collection(ticker)
    count = collection.count()
    if count == 0:
        return []

    n_results = min(top_k, count)
    cutoff = int(
        (datetime.now(timezone.utc) - timedelta(days=max_age_days)).timestamp()
    )

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"published_ts": {"$gte": cutoff}},
    )
    if not results["documents"][0]:
        results = collection.query(query_texts=[query], n_results=n_results)

    return [
        {"text": doc, **meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
