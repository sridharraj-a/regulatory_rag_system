import json

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

from app.core.logger import logger
from app.schema.query_response import (
    Citation,
    LLMAnswer,
    QueryResponse,
    RetrievalResult,
    RetrievedDocument,
    UserQueryResponse,
)
from app.tools.tools import (
    search_fts,
    search_hybrid,
    search_vector,
)


class RagAgent:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-5.5",
            temperature=0,
        )

        self.regulatory_agent = create_agent(
            model=self.llm,
            tools=[
                search_vector,
                search_fts,
                search_hybrid,
            ],
            response_format=LLMAnswer,
            system_prompt="""You are a Banking Regulatory FAQ Assistant.

Your purpose is to provide a concise and accurate answer user questions
using only the available regulatory documents in a direct manner.

Your workflow is fixed and must be followed exactly.

=========================
STEP 1 - Analyze Query
=========================

Analyze the user's question to determine the most appropriate retrieval strategy.

If the user's question is unrelated to banking or banking regulations:

- Do not call any retrieval tool.
- Respond directly with the structured response.
- Leave retrieval empty.

Choose exactly ONE retrieval tool.

Use:

• search_vector
For conceptual questions requiring explanation, comparison, summaries, intent or meaning.

• search_fts
For questions containing exact searchable identifiers.

• search_hybrid
When the question contains both conceptual language and exact identifiers.

=========================
STEP 2 - Retrieval
=========================

Call exactly ONE retrieval tool.

Never call more than one tool.

=========================
STEP 3 - Generate Answer
=========================

Generate the answer ONLY from the retrieved content.

Do not use external knowledge.

If the answer is not present in the retrieved documents, respond exactly:

"I could not find this information in the available regulatory documents."

Return only the structured response.
""",
        )

    def invoke(self, query: str):

        try:

            logger.info("========== RAG AGENT STARTED ==========")
            logger.info("Processing query: %s", query)

            result = self.regulatory_agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": query,
                        }
                    ]
                }
            )

            logger.info("Agent invoked successfully.")

            llm_response = result["structured_response"]

            tool_messages = [
                message
                for message in result["messages"]
                if isinstance(message, ToolMessage)
            ]

            if len(tool_messages) == 0:

                logger.info("No retrieval tool selected.")

                retrieval = RetrievalResult(
                    retrieval_strategy="NONE",
                    documents=[],
                )

            elif len(tool_messages) == 1:

                logger.info(
                    "Retrieval strategy: %s",
                    tool_messages[0].name,
                )

                tool_output = json.loads(tool_messages[0].content)

                retrieval = RetrievalResult(
                    retrieval_strategy=tool_messages[0].name,
                    documents=[
                        RetrievedDocument.model_validate(doc)
                        for doc in tool_output["documents"]
                    ],
                )

            else:

                raise RuntimeError(
                    f"Expected at most one retrieval tool call, found {len(tool_messages)}."
                )

            citations = self.build_citations(
                retrieval.documents
            )

            query_response = QueryResponse(
                answer=llm_response.answer,
                rule_summary=llm_response.rule_summary,
                citations=citations,
                confidence_score=self.calculate_confidence(
                    retrieval
                ),
                disclaimer=(
                    "This response is generated from the retrieved regulatory documents "
                    "and is intended for informational purposes only. "
                    "It should not be considered legal, regulatory, or compliance advice. "
                    "Always refer to official regulator publications before making compliance decisions."
                ),
            )

            logger.info("========== RAG AGENT COMPLETED ==========")

            return UserQueryResponse(
                retrieval=retrieval,
                query_response=query_response,
            )

        except Exception as e:

            logger.exception("RAG Agent execution failed.")

            raise RuntimeError(
                f"Agent execution failed: {str(e)}"
            ) from e

    def build_citations(self, documents: list[RetrievedDocument]):

        logger.info("Building citations.")

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

        logger.info("Generated %s citations.", len(citations))

        return citations

    def calculate_confidence(
        self,
        retrieval: RetrievalResult,
    ):

        logger.info("Calculating confidence score.")

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

        confidence = (
            0.6 * top_score
            + 0.3 * avg_score
            + 0.1 * coverage
        )

        confidence = 0.5 + (confidence * 0.5)

        confidence = round(confidence, 2)

        logger.info(
            "Confidence Score: %.2f",
            confidence,
        )

        return confidence