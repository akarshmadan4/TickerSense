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
            {"title": a["title"], "publisher": a["publisher"], "link": a["link"]}
            for _, a in new
        ],
    )


def retrieve_relevant_news(ticker: str, query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k articles for this ticker most relevant to `query`."""
    collection = _get_collection(ticker)
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query], n_results=min(top_k, collection.count())
    )

    return [
        {"text": doc, **meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
