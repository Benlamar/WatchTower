from celery import Celery
from service.StreamingService import StreamRunner
from random import random

c_tasker = Celery("tasker", broker="redis://localhost:6379/")

@c_tasker.task
async def startTasker():
    # stamp = random.randint(50, 120)
    # runner = StreamRunner("Task"+str(stamp), stamp)
    # await runner.start()
    pass

