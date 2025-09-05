from redis import Redis

import constants

REDIS_CONNECTION = Redis().from_url(constants.REDIS_CONN_STRING)
