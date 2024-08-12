from celery import Celery
from service.StreamingService import StreamServiveRunner
from time import sleep
import asyncio
c_tasker = Celery("tasker", broker="redis://localhost:6379/")

@c_tasker.task
def startTasker(*args):
    # await asyncio.sleep(5)
    for _ in range(5):
        sleep(1)
    print("Hello -- >", args)
    # print("Args ---> : ",s, r, n)

    # runner = StreamServiveRunner()
    # await runner.start()