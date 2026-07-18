from fastapi import APIRouter

from app.schema.query_request import QueryRequest
from app.services.query_service import QueryService

router = APIRouter(
    prefix="/query",
    tags=["Query"],
)

service = QueryService()


@router.post("/")
def query(request: QueryRequest):

    result = service.query(request.query)

    return result.query_response


@router.post("/debug")
def query_debug(request: QueryRequest):

    return service.query(request.query)
