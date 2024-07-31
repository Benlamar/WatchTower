from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from crud.camera import queryAllCamera, queryInsertCamera
from schemas.camera import CreateCamera, DeleteCamera 

def getAllCamera(db:Session):
    try:
        cameras = queryAllCamera(db)
        return cameras
    except:
        raise HTTPException(status_code=500, detail="Failed to query all camera")

def createCamera(cam_data: CreateCamera, db:Session):
    print("Data to insert ; ", cam_data)
    try:
        create_cam = queryInsertCamera(cam_data, db)
        if create_cam is None:
            return None
        else:
            return CreateCamera(**create_cam)
    except:
        raise HTTPException(status_code=500, detail="Failed toquery add camera")

def removeCamera(cam_id: DeleteCamera, db:Session):
    pass

def updateCamera(db:Session):
    pass
