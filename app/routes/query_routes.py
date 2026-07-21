from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.schema.query_request import QueryRequest
from app.schema.query_response import (
    QueryResponse,
    UserQueryResponse,
)
from app.services.query_service import QueryService

router = APIRouter(
    prefix="/api/v1/query",
    tags=["Query"],
)

service = QueryService()


@router.post(
    "/",
    response_model=QueryResponse,
)
def query(request: QueryRequest):

    try:

        logger.info("Received query request.")

        result = service.query(request.query)

        logger.info("Query completed successfully.")

        return result.query_response

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Query endpoint failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        ) from e


@router.post(
    "/debug",
    response_model=UserQueryResponse,
)
def query_debug(request: QueryRequest):

    try:

        logger.info("Received debug query request.")

        result = service.query(request.query)

        logger.info("Debug query completed successfully.")

        return result

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Debug endpoint failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        ) from e