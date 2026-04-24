from rq import Worker
from app.core.queue import redis_conn
from app.core.config import settings


if __name__ == "__main__":
    worker = Worker([settings.APP_NAME], connection=redis_conn)
    worker.work()