from fastapi import APIRouter
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

    result = service.query(request.query)

    return result.query_response


@router.post(
    "/debug",
    response_model=UserQueryResponse,
)
def query_debug(request: QueryRequest):

    return service.query(request.query)
