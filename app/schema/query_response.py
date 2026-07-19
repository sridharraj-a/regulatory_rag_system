from pydantic import BaseModel, Field
from typing import Literal, List, Any
from uuid import UUID

# class QueryAnalysis(BaseModel):
#    intent: str
#    retrieval_strategy: str
#    search_terms: list[str]
#    semantic_query: str
#    metadata_filters: dict
#    reasoning: str


class QueryAnalysis(BaseModel):
    #    intent: str
    retrieval_strategy: Literal["VECTOR", "FTS", "HYBRID"]
    search_terms: list[str]
    semantic_query: str


#    entities: list[str]
#    metadata_filters: dict
#    reasoning: str


class Citation(BaseModel):
    source: str = Field(description="Document name")
    page: int | None = Field(default=None)
    section: str | None = Field(default=None)
    excerpt: str | None = Field(default=None)


class QueryResponse(BaseModel):
    #    query: str
    answer: str
    citations: List[Citation]
    rule_summary: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)


#
#    disclaimer: str
#    retrieval_strategy: str
#    langsmith_trace_id: str | None = None


class RetrievedDocument(BaseModel):
    content: str
    metadata: dict[str, Any]
    fts_rank: float | None = None


class RetrievalResult(BaseModel):
    retrieval_strategy: str
    semantic_query: str
    search_terms: list[str]
    documents: list[RetrievedDocument]


class UserQueryResponse(BaseModel):
    analysis: QueryAnalysis
    retrieval: RetrievalResult
    query_response: QueryResponse


class LLMAnswer(BaseModel):
    answer: str
    rule_summary: list[str]
