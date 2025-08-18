from redis import Redis
from rq import Queue
import constants

queue = Queue(connection=Redis().from_url(constants.REDIS_HOST))
