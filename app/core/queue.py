import redis
from rq import Queue
from app.core.config import settings


redis_conn = redis.from_url(settings.REDIS_URL) # type: ignore

queue = Queue(settings.APP_NAME, connection=redis_conn)