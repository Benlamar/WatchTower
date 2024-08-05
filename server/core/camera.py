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
    try:
        create = queryInsertCamera(cam_data, db)
        if create is None:
            return None
        else:
            return CreateCamera(cam_name = create.cam_name, 
                                location = create.location,
                                ip_address = create.ip_address)
    except:
        raise HTTPException(status_code=500, detail="Failed to query add camera")

def removeCamera(cam_id: DeleteCamera, db:Session):
    pass

def updateCamera(db:Session):
    pass
