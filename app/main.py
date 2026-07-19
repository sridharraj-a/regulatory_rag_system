from fastapi import FastAPI

from app.routes.query_routes import router as query_router

from app.upload_routes import router as upload_router




app = FastAPI(
    title="Regulatory RAG System",
    version="1.0.0",
)
@app.get("/")
def home():

    return {
        "message":
        "Regulatory Compliance RAG System Running"
    }

app.include_router(query_router)

app.include_router(
    upload_router
)





















