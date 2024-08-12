from celery import Celery
from service.StreamingService import StreamServiveRunner
import asyncio

c_tasker = Celery("tasker", broker="redis://localhost:6379/")

@c_tasker.task
def startTasker(**kwargs):
    runner = StreamServiveRunner(source=kwargs["source"], room_id=kwargs["room_id"], stream_name=kwargs["stream_name"])
    asyncio.run(runner.start())