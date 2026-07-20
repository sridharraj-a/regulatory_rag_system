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
    print("RETRIEVED DOCUMENTS")
    print("==============================")

    for i, doc in enumerate(result.retrieval.documents, start=1):

        print(f"\nDocument {i}")
        print(f"Source    : {doc.metadata.get('source')}")
        print(f"Metadata  : {doc.metadata}")
        print(f"Score     : {doc.retrieval_score}")
        print(f"Type      : {doc.score_type}")
        print(f"Content   : {doc.content[:300]}")

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(result.query_response.answer)

    print("\nRule Summary")

    for rule in result.query_response.rule_summary:
        print(f"- {rule}")

    print("\nCitations")

    for citation in result.query_response.citations:
        print(f"- Source : {citation.source}")
        print(f"  Page   : {citation.page}")
        print(f"  Section: {citation.section}")
        print(f"  Text   : {citation.excerpt}")
        print()

    print("\nConfidence")

    print(result.query_response.confidence_score)


if __name__ == "__main__":
    main()
