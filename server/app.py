from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api import auth, users, camera
from db.database import startDB
from contextlib import asynccontextmanager
from service.Tasker import startTasker, revokeTask
from core.settings import setting

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Attempt to start the database
        startDB()
        yield
    except Exception as e:
        print(f"Failed to start the database: {e}")
        raise HTTPException(status_code=500, detail="Failed to start the database")
    finally:
        print("Application is stopping")


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(camera.router, prefix="/camera", tags=["camera"])


# This is for the sake of testing only
# @app.get("/start")
# def getStart():
#     kwargs = {"source": 0, "room_id":setting.ROOM_ID, "stream_name": "Web Cam"}
#     task_id = startTasker.delay(**kwargs)
#     return "OK "+str(task_id)


# This is for the sake of testing only
# @app.post('/stop_task')
# def stopTask(task_id:str):
#     res = revokeTask(task_id)
#     # print("Celery response --->", res)
#     return res
    