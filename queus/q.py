from redis import Redis
from rq import Queue
import constants
from base import REDIS_CONNECTION

queue = Queue(connection=REDIS_CONNECTION)
