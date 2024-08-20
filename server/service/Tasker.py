import asyncio
import os
from celery import Celery
from celery.result import AsyncResult
from service.StreamingService import StreamServiveRunner
from time import sleep

c_tasker = Celery("tasker", broker=os.getenv("REDIS_URL"))

@c_tasker.task
def startTasker(**kwargs):
    print("Kwargs : ",kwargs)
    for i in range(5):
        print("tasker", i)
        sleep(1)
    # runner = StreamServiveRunner(source=kwargs["source"], room_id=kwargs["room_id"], stream_name=kwargs["stream_name"])
    # asyncio.run(runner.start())

def revokeTask(task:str):
    task_result = AsyncResult(id=task, app=c_tasker)

    if not task_result:
        return False
    if task_result.state == 'PENDING':
        task_result.revoke(terminate=True)
    elif task_result.state == 'STARTED':
        task_result.revoke(terminate=True)
    elif task_result.state == 'PROGRESS':
        task_result.revoke(terminate=True)
    
    return True
