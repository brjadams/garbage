#!/usr/bin/env python
from redisconnect import Redis
from rq import Worker

# Preload libraries

# Provide the worker with the list of queues (str) to listen to.
w = Worker(['default'], connection=Redis(), name="count_words_worker")
w.work()