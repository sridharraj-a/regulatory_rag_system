from fastapi import HTTPException

from app.agents.rag_agent import RagAgent
from app.core.logger import logger


class QueryService:

    def __init__(self):

        self.agent = RagAgent()

    def query(self, query: str):

        try:

            logger.info("========== QUERY STARTED ==========")

            if not query.strip():

                raise HTTPException(status_code=400, detail="Query cannot be empty.")

            logger.info("User Query: %s", query)

            response = self.agent.invoke(query)

            logger.info("========== QUERY COMPLETED ==========")

            return response

        except HTTPException:
            raise

        except Exception as e:

            logger.exception("Query Service failed.")

            raise HTTPException(
                status_code=500, detail=f"Query processing failed: {str(e)}"
            ) from e
