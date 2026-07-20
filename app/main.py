from fastapi import FastAPI

from app.routes.query_routes import router as query_router

from app.routes.upload_routes import router as upload_router

app = FastAPI(
    title="Regulatory RAG System",
    version="1.0.0",
)


@app.get("/", tags=["System"])
def root():
    return {"service": "Regulatory RAG System", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():

    return {"status": "UP"}


@app.get("/version")
def version():

    return {
        "service": "Regulatory RAG System",
        "version": "1.0.0",
        "environment": "DEV",
    }


app.include_router(query_router)

app.include_router(upload_router)
