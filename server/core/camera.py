from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from crud.camera import (queryAllCamera, queryInsertCamera, 
                         queryUpdateCameraTask, queryUpdateCameraBoundary, 
                         queryRemoveCamera)
from schemas.camera import (CreateCamera, DeleteCamera, 
                            UpdateCameraTask, UpdateCameraBorder, 
                            CamerasInDB, CameraError)
from service.Tasker import startTasker, revokeTask
from core.settings import setting

def getAllCamera(db:Session):
    try:
        cameras = queryAllCamera(db)
        return cameras
    except:
        raise HTTPException(status_code=500, detail="Failed to query all camera")

def createCamera(cam_data: CreateCamera, db:Session):
    try:
        create = queryInsertCamera(cam_data, db)
        if create is None:
            return None
        else:
            # start Camera streaming
            kwargs = {"source": 0, "room_id":setting.ROOM_ID, "stream_name": create.cam_name}
            task_id = startTasker.delay(**kwargs)
            #  start task here
            add_task = queryUpdateCameraTask(UpdateCameraTask(id=int(create.id), task=str(task_id)), db)
            if not add_task:
               delete_cam = queryRemoveCamera(DeleteCamera(id=create.id))
               if delete_cam is None:
                   raise Exception("Failed to start task and remove camera")
               return None
             
            return CamerasInDB( id=create.id,
                                cam_name = create.cam_name, 
                                location = create.location,
                                source=create.source,
                               )
    except Exception as e:
        print(f"Error in createCamera: {e}")
        raise HTTPException(status_code=400, detail="Failed to query add camera")

def removeCamera(cam_del: int, db:Session):
    try:
        cam_remove = queryRemoveCamera(cam_del, db)
        if cam_remove:
            return CamerasInDB(id=cam_remove.id, cam_name=cam_remove.cam_name,
                              location=cam_remove.location, source=cam_remove.source)
        else:
            return None
    except Exception as e:
        print(f"Error in remove Camera {e}")
        raise HTTPException(status_code=500, detail="Failed to remove camera")

def updateCameraBoundary(boundary: UpdateCameraBorder, db:Session):
    try:
        boundary = queryUpdateCameraBoundary(boundary, db)
        if not boundary:
            return None
        return CamerasInDB(id=int(boundary.id), cam_name=boundary.cam_name, 
                           location=boundary.location, source=boundary.source)
    except Exception as e:
        print(f"Error in update camera boundary : {e}")
        raise HTTPException(status_code=500, detail="Failed to add boundary camera")
