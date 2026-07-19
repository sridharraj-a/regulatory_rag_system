from app.schema.query_response import (
    QueryAnalysis,
    RetrievedDocument,
    QueryResponse,
    RetrievalResult,
    UserQueryResponse,
    Citation,
    LLMAnswer,
)

from app.tools.tools import (
    search_vector,
    search_fts,
    search_hybrid,
)

from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langsmith import traceable


class RagAgent:

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5.5", temperature=0)

        self.query_identification_agent = create_agent(
            model="openai:gpt-5.5",  # brain of the agent
            # model=self.llm,  # brain of the agent
            tools=[],
            response_format=QueryAnalysis,
            system_prompt="""
            You are the Retrieval Planner for a Banking Regulatory Knowledge Base.

            Your only task is to prepare a user's query for retrieval.

            For each query produce:

            1. semantic_query
            - Rewrite the question for semantic retrieval.
            - Preserve intent and regulatory meaning.
            - Expand abbreviations only when helpful.

            2. search_terms
            Extract exact searchable terms including:
            - regulatory acronyms
            - regulation, framework and Act names
            - circular, section or clause numbers
            - dates
            - percentages
            - monetary values
            - proper nouns

            3. strategy
            Choose one:
            - VECTOR: conceptual questions (what, why, how, explanation, comparison, summary)
            - FTS: exact identifiers (acronyms, regulation names, circulars, sections, dates, percentages)
            - HYBRID: contains both conceptual language and exact identifiers.

            Return only JSON matching the QueryAnalysis schema.""",
            # roles and goals
        )

        self.answer_generation_agent = create_agent(
            # model="openai:gpt-5.5",
            model=self.llm,  # brain of the agent
            tools=[],
            response_format=LLMAnswer,
            system_prompt="""
            You are a Banking Regulatory Response Generator.

            Answer only using the retrieved regulatory documents.

            Return:

            1. answer
            - Provide a concise regulatory response.

            2. rule_summary
            - Extract key rules, limits or thresholds.

            Do not generate citations.
            Do not generate page numbers.
            Do not generate confidence scores.

            Return only the structured response.

            """,
        )

    def invoke(self, query: str):

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )

        analysis = self.identify_query(query)

        retrieval = self.retrieve_documents(analysis)

        context = self.build_context(retrieval)

        llm_response = self.generate_answer(
            query, context, retrieval.retrieval_strategy
        )

        citations = self.build_citations(retrieval.documents)

        query_response = QueryResponse(
            answer=llm_response.answer,
            rule_summary=llm_response.rule_summary,
            citations=citations,
            confidence_score=self.calculate_confidence(retrieval),
        )

        return UserQueryResponse(
            analysis=analysis,
            retrieval=retrieval,
            query_response=query_response,
        )

    @traceable(name="Identify Query Agent")
    def identify_query(self, query: str) -> QueryAnalysis:

        response = self.query_identification_agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        return response["structured_response"]

    def retrieve_documents(self, analysis: QueryAnalysis) -> RetrievalResult:
        """
        Execute the appropriate retrieval strategy and
        return the retrieved documents.
        """

        strategy = analysis.retrieval_strategy

        if strategy == "VECTOR":
            docs = search_vector(analysis.semantic_query)

        elif strategy == "FTS":
            docs = search_fts(" ".join(analysis.search_terms))

        elif strategy == "HYBRID":
            docs = search_hybrid(
                analysis.semantic_query,
                analysis.search_terms,
            )

        else:
            raise ValueError(f"Unknown retrieval strategy: {strategy}")

        return RetrievalResult(
            retrieval_strategy=strategy,
            semantic_query=analysis.semantic_query,
            search_terms=analysis.search_terms,
            documents=[RetrievedDocument(**doc) for doc in docs],
        )

    def build_context(self, result: RetrievalResult):

        context = ""

        for i, doc in enumerate(result.documents, start=1):

            context += f"""
            Document {i}
            Content: {doc.content}
            Metadata:{doc.metadata}
            """

        return context

    @traceable(name="Answer Gen Agent")
    def generate_answer(self, query, context, strategy):
        answer = self.answer_generation_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
        User Question :  {query}
        Retrieved Documents : {context}
        Retrieval Strategy : {strategy} 
        """,
                    }
                ]
            }
        )
        return answer["structured_response"]

    def build_citations(self, documents: list[RetrievedDocument]):
        seen = set()
        citations = []

        for doc in documents:

            metadata = doc.metadata

            key = (
                metadata.get("source"),
                metadata.get("page"),
                metadata.get("section"),
            )

            if key in seen:
                continue

            seen.add(key)

            citations.append(
                Citation(
                    source=metadata.get("source", "Unknown Source"),
                    page=metadata.get("page", 0) + 1,
                    section=metadata.get("section", ""),
                    excerpt=doc.content[:250].strip(),
                )
            )
        return citations

    def calculate_confidence(self, retrieval: RetrievalResult):

        scores = [
            doc.retrieval_score
            for doc in retrieval.documents
            if doc.retrieval_score is not None
        ]

        if not scores:
            return 0.0

        top_score = max(scores)

        avg_score = sum(scores) / len(scores)

        coverage = min(len(scores) / 5, 1)

        confidence = 0.6 * top_score + 0.3 * avg_score + 0.1 * coverage

        # compress extreme differences
        confidence = 0.5 + (confidence * 0.5)
        return round(confidence, 2)
