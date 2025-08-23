from fastapi import APIRouter, FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from rq.job import Job
from rq_dashboard_fast import RedisQueueDashboard

from redisconnect import REDIS_CONNECTION

job_router = APIRouter(prefix="/job", tags=["jobs"])


@job_router.get("/{job_id}")
async def get_job_status(job_id: str):
    job = Job.fetch(job_id, connection=REDIS_CONNECTION)
    return {"id": job.id, "status": job.get_status(), "result": job.result}
