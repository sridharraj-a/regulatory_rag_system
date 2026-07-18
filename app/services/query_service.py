from app.agents.rag_agent import RagAgent


class QueryService:

    def __init__(self):

        self.agent = RagAgent()

    def query(self, query: str):

        return self.agent.invoke(query)
