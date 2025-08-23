# ...existing code...
import asyncio
import os

import pandas as pd
import requests
import rich
from redis import Redis, exceptions
from redis.commands.json.decoders import decode_list, unstring
from redis.commands.json.path import Path
from rich import print
from rq import Retry

from redisconnect import REDIS_CONNECTION


async def csv_to_json_redis(
    file: str = "", max=1, interval=60
):  # Adjust parameters as needed
    try:
        df = pd.read_csv(file, delimiter="\t")
        hash = os.path.splitext(os.path.basename(file))[0]
        json = df.to_json(orient="records")
        REDIS_CONNECTION.json().set(hash, Path.root_path(), json)
    except requests.exceptions.ConnectionError:
        return Retry(max=max, interval=interval)
    return {
        "status": 200,
        "file": str(file),
        "hash": str(hash),
        "message": f"{len(df)} rows of CSV data from {file} stored in Redis.",
    }


async def embed_documents(hash: str = ""):  # Adjust parameters as needed
    from llm.model import main as model_main
    import json
    redis_json = REDIS_CONNECTION.json().get(hash, Path.root_path())
    rich.print(f"Retrieved JSON, type{type(redis_json)}, data for hash {hash}: {redis_json}")
    data = await model_main(data=json.loads(json.dumps(redis_json)), hash=hash)
    return {
        "status": 200,
        "hash": str(hash),
        "message": f"Embedding process completed for hash {hash}.",
    }


def count_words_at_url(url):
    """Just an example function that's called async."""
    resp = requests.get(url)
    return len(resp.text.split())


def report_success(job, connection, result, *args, **kwargs):
    print(f"Job {job.id} completed successfully with result: {result}")
    REDIS_CONNECTION.publish("job_notifications", f"Job {job.id} completed successfully.")
