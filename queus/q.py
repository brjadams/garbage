from rq import Queue

from redisconnect import REDIS_CONNECTION

queue = Queue(connection=REDIS_CONNECTION)
csv_to_db_q = Queue(name="csv_to_db", connection=REDIS_CONNECTION)
csv_to_redis_json = Queue(name="csv_to_redis_json", connection=REDIS_CONNECTION)
embed_doc = Queue(name="embed_doc", connection=REDIS_CONNECTION)
