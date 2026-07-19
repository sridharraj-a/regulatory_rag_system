import psycopg
import os
from app.core.db import get_vector_store
from psycopg.rows import dict_row
from langsmith import traceable

# PGVector connection string uses SQLAlchemy format: postgresql+psycopg://...
# psycopg.connect needs standard format: postgresql://...
_raw_conn = os.getenv("PG_CONNECTION_STRING_FTS")
RETRIEVAL_K = 20
RETURN_K = 5


@traceable(name="FTS Search")
def search_fts(
    query: str, k: int = RETRIEVAL_K, collection_name: str = "reg_support_desk"
):
    """Keyword search against the stored chunks using Postgres' tsvector/tsquery/ts_rank"""
    sql = """
       SELECT
           e.document                                               AS content,
           e.cmetadata                                              AS metadata,
           ts_rank(
               to_tsvector('english', e.document),
               plainto_tsquery('english', %(query)s)
           )                                                        AS fts_rank
       FROM  langchain_pg_embedding  e
       JOIN  langchain_pg_collection c ON c.uuid = e.collection_id
       WHERE c.name = %(collection)s
         AND to_tsvector('english', e.document)
             @@ plainto_tsquery('english', %(query)s)
       ORDER BY fts_rank DESC
       LIMIT %(k)s;
   """

    with psycopg.connect(_raw_conn, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"query": query, "collection": collection_name, "k": k})
            rows = cur.fetchall()

    output = [
        {
            "content": row["content"],
            "metadata": row["metadata"],
            "fts_rank": round(float(row["fts_rank"]), 4),
        }
        for row in rows
    ]

    # print(output)
    # return output
    return _sort_by_freshness(output)


@traceable(name="Vector Search")
def search_vector(
    query: str, k: int = RETRIEVAL_K, collection_name: str = "reg_support_desk"
):
    """performs Vector Search"""
    vector_store = get_vector_store(collection_name)
    docs = vector_store.similarity_search(query, k)

    output = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in docs
    ]

    # print(output)
    # return output
    return _sort_by_freshness(output)


@traceable(name="Hybrid Search")
def search_hybrid(
    semantic_query: str,
    search_terms: list[str],
    k: int = RETRIEVAL_K,
    collection_name: str = "reg_support_desk",
):
    """Merge vector and fts results using RRF (Reciprocal Rank Fusion)
    Chunks appearing in both search results will rank higher than those in only one
    The constant 60 prevents top-ranked outputs from dominating
    How RRF scores for a chunk = sum of 1/(rank + 60)
    """
    # print("Running Hybrid Search")

    vector_search_results = search_vector(
        semantic_query,
        k,
        collection_name,
    )

    fts_results = search_fts(
        " ".join(search_terms),
        k,
        collection_name,
    )

    rrf_scores: dict[str, float] = {}
    chunk_map: dict[str, dict] = {}

    # Walk the vector results in ranked order (best match first).
    # enumerate gives rank 0, 1, 2... so we add +1 below to make ranks start at 1.
    for rank, doc in enumerate(vector_search_results):
        # Use the first 120 chars of the chunk text as an identity key.
        # Same chunk retrieved by both searches -> same key -> its scores add up.
        key = doc["content"][:120]
        # RRF formula: score += 1 / (k_constant + rank). Better rank (smaller number)
        # gives a bigger score. .get(key, 0) lets us accumulate across both loops.
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank + 1)
        # Remember the full chunk so we can rebuild the final list from the winning keys.
        chunk_map[key] = {"content": doc["content"], "metadata": doc["metadata"]}

    # Same pass over the FTS results. A chunk found by BOTH searches gets scored
    # twice here, which is exactly how RRF rewards agreement between the two methods.
    for rank, item in enumerate(fts_results):
        key = item["content"][:120]
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank + 1)
        chunk_map[key] = {"content": item["content"], "metadata": item["metadata"]}

    # this sorts the results of our RRF calculation so that, the higher scoring
    # doc will be ordered from higher rank to lower
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    # print(ranked)
    documents = [chunk_map[key] for key, _ in ranked[:k]]
    return _sort_by_freshness(documents)


def _sort_by_freshness(documents: list[dict]) -> list[dict]:
    """
    Sort documents by last_updated (newest first)
    and return only the top RETURN_K.
    """
    return sorted(
        documents,
        key=lambda doc: float(doc["metadata"].get("last_updated", 0)),
        reverse=True,
    )[:RETURN_K]
