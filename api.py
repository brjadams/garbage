from fastapi import APIRouter, FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from rq_dashboard_fast import RedisQueueDashboard

import constants
from routers.jobs import jobs


# Define a model for document processing input
class Document(BaseModel):
    content: str
    
app = FastAPI()

dashboard = RedisQueueDashboard(constants.REDIS_HOST, "/rq")
app.mount("/rq", dashboard)
process_router = APIRouter(prefix="/process", tags=["document_processing"])

mcp = FastApiMCP(app)
mcp.mount()


# Liveness probe endpoint
@app.get("/healthz", operation_id="liveness_probe")
def liveness_probe():
    """
    Liveness probe endpoint for Kubernetes.
    Always returns 200 OK if the application is running.
    """
    return {"status": "OK"}

# Readiness probe endpoint
@app.get("/readyz", operation_id="readiness_probe")
def readiness_probe():
    """
    Readiness probe endpoint for Kubernetes.
    Add logic to check if the application is ready (e.g., database connection, external API availability).
    """
    is_ready = True  # Replace with actual readiness logic
    if is_ready:
        return {"status": "READY"}
    else:
        return {"status": "NOT READY"}


@process_router.get("/document/")
def process_document():
    """
    Endpoint to process a document.
    Accepts a JSON payload with the document content.
    """
    # if not document.content:
    #     raise HTTPException(status_code=400, detail="Document content cannot be empty")
    
    # Example processing: Count the number of words in the document
    # word_count = len(document.content.split())
    print("Processing document...")
    from queus.jobs import count_words_at_url
    from queus.q import queue
    job = queue.enqueue(count_words_at_url, 'https://www.landsend.com')
    return {"job": job.started_at, "message": "Document processed successfully"}



app.include_router(process_router)
