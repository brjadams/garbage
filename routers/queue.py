from fastapi import APIRouter
from rq.job import Queue

from redisconnect import REDIS_CONNECTION

q_router = APIRouter(prefix="/job", tags=["jobs"])



@q_router.get("/queue/{queue_name}")
def list_jobs_by_queue(queue_name: str):
    queue = Queue(queue_name, connection=REDIS_CONNECTION)
    jobs = [
        {"id": job.id, "status": job.get_status(), "result": job.result}
        for job in queue.jobs
    ]
    return {"queue": queue_name, "jobs": jobs}


@q_router.get("/queues")
def list_queues():
    queues = Queue.all(connection=REDIS_CONNECTION)
    return [q.name for q in queues]
