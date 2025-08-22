from fastapi import APIRouter, FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from rq.job import Job
from rq_dashboard_fast import RedisQueueDashboard

from redis import Redis

from .. import constants
from ..redis import REDIS_CONNECTION as redis_conn

job_router = APIRouter(prefix="/job", tags=["jobs"])


@job_router.get("/job/{job_id}")
def get_job_status(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)
    return {"id": job.id, "status": job.get_status(), "result": job.result}
