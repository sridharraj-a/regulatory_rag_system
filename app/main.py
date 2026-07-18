from fastapi import FastAPI

from app.routes.query_routes import router as query_router

app = FastAPI(
    title="Regulatory RAG System",
    version="1.0.0",
)

app.include_router(query_router)
