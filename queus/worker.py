#!/usr/bin/env python
from redisconnect import Redis
from rq import Worker

# Preload libraries
from jobs import count_words_at_url  # Ensure jobs are loaded before starting the worker

# Provide the worker with the list of queues (str) to listen to.
w = Worker(['default'], connection=Redis(), name="count_words_worker")
w.work()