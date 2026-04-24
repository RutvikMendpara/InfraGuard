from rq import Worker
from app.core.queue import redis_conn
from app.core.config import settings
from threading import Thread
from app.workers.scheduler import start_scheduler

if __name__ == "__main__":
    Thread(target=start_scheduler, daemon=True).start()
    worker = Worker([settings.APP_NAME], connection=redis_conn)
    worker.work()