from app.services.query_service import QueryService


def main():

    service = QueryService()

    query = input("Question: ")

    result = service.query(query)

    print("\n==============================")
    print("QUERY")
    print("==============================")
    print(query)

    print("\n==============================")
    print("QUERY ANALYSIS")
    print("==============================")
    print(f"Strategy      : {result.analysis.retrieval_strategy}")
    print(f"Semantic Query: {result.analysis.semantic_query}")
    print(f"Search Terms  : {', '.join(result.analysis.search_terms)}")

    print("\n==============================")
    print("RETRIEVED DOCUMENTS")
    print("==============================")

    for i, doc in enumerate(result.retrieval.documents, start=1):

        print(f"\nDocument {i}")
        print(f"Source    : {doc.metadata.get('source')}")
        print(f"Metadata  : {doc.metadata}")
        print(f"Content   : {doc.content[:300]}")

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(result.response.answer)

    print("\nRule Summary")
    print(result.response.rule_summary)

    print("\nCitations")

    for citation in result.response.citations:
        print(f"- {citation}")

    print("\nConfidence")

    print(result.response.confidence_score)


if __name__ == "__main__":
    main()
