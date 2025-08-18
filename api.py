import constants
from fastapi import FastAPI, HTTPException, APIRouter
from rq_dashboard_fast import RedisQueueDashboard
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

# Define a model for document processing input
class Document(BaseModel):
    content: str
    
app = FastAPI()

dashboard = RedisQueueDashboard(constants.REDIS_HOST, "/rq")
app.mount("/rq", dashboard)
router = APIRouter(prefix="/process", tags=["document_processing"])

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


@router.post("/document/")
def process_document(document: Document):
    """
    Endpoint to process a document.
    Accepts a JSON payload with the document content.
    """
    if not document.content:
        raise HTTPException(status_code=400, detail="Document content cannot be empty")
    
    # Example processing: Count the number of words in the document
    word_count = len(document.content.split())
    return {"word_count": word_count, "message": "Document processed successfully"}