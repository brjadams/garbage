from fastapi import APIRouter, FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from rq.job import Job, Queue
from rq_dashboard_fast import RedisQueueDashboard

import constants
import redis

q_router = APIRouter(prefix="/job", tags=["jobs"])
redis_conn = redis.Redis()

@q_router.get("/queue/{queue_name}")
def list_jobs_by_queue(queue_name: str):
    queue = Queue(queue_name, connection=redis_conn)
    jobs = [
        {
            "id": job.id,
            "status": job.get_status(),
            "result": job.result
        }
        for job in queue.jobs
    ]
    return {"queue": queue_name, "jobs": jobs}

@q_router.get("/queues")
def list_queues():
    queues = Queue.all(connection=redis_conn)
    return [q.name for q in queues]