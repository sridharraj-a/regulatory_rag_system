import psycopg
import os
from langchain_core.tools import tool
from app.core.db import get_vector_store
from psycopg.rows import dict_row

# from langsmith import traceable

# PGVector connection string uses SQLAlchemy format: postgresql+psycopg://...
# psycopg.connect needs standard format: postgresql://...
_raw_conn = os.getenv("PG_CONNECTION_STRING_FTS")
RETRIEVAL_K = 5
RETURN_K = 5


# @traceable(name="FTS Search")
def _search_fts(
    query: str, k: int = RETRIEVAL_K, collection_name: str = "reg_support_desk"
):
    """
    Use ONLY for exact regulatory terminology,
    circular names,
    abbreviations,
    percentages,
    section numbers,
    clauses.
    """
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

    output = []

    for row in rows:

        raw_score = float(row["fts_rank"])

        normalized_score = min(raw_score / 0.5, 1.0)

        output.append(
            {
                "content": row["content"],
                "metadata": row["metadata"],
                "retrieval_score": round(normalized_score, 4),
                "score_type": "FTS",
            }
        )
    return {"documents": _sort_by_freshness(output)}


search_fts = tool(_search_fts)


# @traceable(name="Vector Search")
def _search_vector(
    query: str, k: int = RETRIEVAL_K, collection_name: str = "reg_support_desk"
):
    """
    Use ONLY for semantic or conceptual questions (what, why, how, explanation, comparison, summary).
    Never use if the question contains specific regulatory terms,
    numbers, clauses or abbreviations."""
    vector_store = get_vector_store(collection_name)
    docs = vector_store.similarity_search_with_score(query, k)

    output = []

    for doc, distance in docs:
        similarity = 1 - float(distance)
        output.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "retrieval_score": round(similarity, 4),
                "score_type": "VECTOR",
            }
        )

    # print(output)
    # return output
    return {"documents": _sort_by_freshness(output)}


search_vector = tool(_search_vector)


# @traceable(name="Hybrid Search")
def _search_hybrid(
    semantic_query: str,
    search_terms: list[str],
    k: int = RETRIEVAL_K,
    collection_name: str = "reg_support_desk",
):
    """
    Use ONLY when the query contains both
    conceptual language and exact regulatory terminology.
    """
    # print("Running Hybrid Search")

    vector_search_results = _search_vector(
        semantic_query,
        k,
        collection_name,
    )["documents"]

    fts_results = _search_fts(
        " ".join(search_terms),
        k,
        collection_name,
    )["documents"]

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
    # Extract RRF values
    rrf_values = [score for _, score in ranked[:k]]

    max_rrf = max(rrf_values)
    min_rrf = min(rrf_values)

    documents = []

    for key, score in ranked[:k]:

        if max_rrf == min_rrf:
            normalized_score = 1.0

        else:
            normalized_score = (score - min_rrf) / (max_rrf - min_rrf)

        documents.append(
            {
                "content": chunk_map[key]["content"],
                "metadata": chunk_map[key]["metadata"],
                "retrieval_score": round(normalized_score, 4),
                "score_type": "HYBRID",
            }
        )
    # documents = [chunk_map[key] for key, _ in ranked[:k]]
    return {"documents": _sort_by_freshness(documents)}


search_hybrid = tool(_search_hybrid)


def _sort_by_freshness(documents: list[dict]) -> list[dict]:
    """
    For regulatory FAQ documents:
    1. Prefer latest updated document
    2. Use retrieval score only within the same document version
    """

    return sorted(
        documents,
        key=lambda doc: (
            float(doc["metadata"].get("last_updated", 0)),
            float(doc.get("retrieval_score", 0)),
        ),
        reverse=True,
    )[:RETURN_K]
