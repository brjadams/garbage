import os
import uuid

import rich
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from rq import Callback
from rq.job import Dependency
from rq_dashboard_fast import RedisQueueDashboard

import constants
from queus.jobs import report_success
from routers.jobs import job_router


# Define a model for document processing input
class Document(BaseModel):
    content: str


app = FastAPI()

dashboard = RedisQueueDashboard(constants.REDIS_CONN_STRING, "/rq")
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


@process_router.post("/document/")
async def upload_csv(file: UploadFile = File(...)):
    """
    Endpoint to upload a large CSV file and enqueue a model job.
    """
    rich.print(f"Received file: {file.filename}, content_type: {file.content_type}")
    # Extract file extension
    file_extension = os.path.splitext(str(file.filename))[1]
    # Generate a unique new filename
    raw_uuid = uuid.uuid4()
    uuid_fn = f"{raw_uuid}{file_extension}"
    file_path = os.path.join(constants.DOCUMENT_UPLOAD_PATH, uuid_fn)
    rich.print(f"Saving file to: {file_path}")
    try:
        # Save the file with the new filename
        import aiofiles

        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024)  # Read in chunks for efficiency
                if not chunk:
                    break
                await buffer.write(chunk)
        from queus.jobs import csv_to_json_redis, embed_documents
        from queus.q import csv_to_db_q, embed_doc

        store_in_redis_as_json = csv_to_db_q.enqueue(
            csv_to_json_redis, file=file_path, on_success=Callback(report_success)
        )

        embed_json_docs_in_vectordb = embed_doc.enqueue(
            embed_documents,
            hash=str(raw_uuid),
            depends_on=store_in_redis_as_json,
            on_success=Callback(report_success),
        )

        return {
            "filename": uuid_fn,
            "content_type": file.content_type,
            "message": "File uploaded successfully! Processing of file has started.",
            "job": {"csv_to_db_job_id": str(store_in_redis_as_json.id), "embed_job_id": str(embed_json_docs_in_vectordb.id)},
        }
    except Exception as E:
        raise HTTPException(
            status_code=500,
            detail={"error": str(E), "message": "Failed to upload file."},
        )
    finally:
        await file.close()


app.include_router(process_router)
app.include_router(job_router)
