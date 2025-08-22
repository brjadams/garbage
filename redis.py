from rq import Queue

import constants
import redis

REDIS_CONNECTION = redis.Redis().from_url(constants.REDIS_HOST)

