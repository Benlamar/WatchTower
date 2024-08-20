from sqlalchemy.orm import Session
from db.models.camera import Camera
from schemas.camera import CreateCamera, UpdateCameraBorder, UpdateCameraTask, DeleteCamera 

def queryAllCamera(db: Session):
    try:
        return db.query(Camera).all()
    except:
        print("Error encountered when tyrying to getAllUsers in curd")
        return []
    
def queryInsertCamera(data: CreateCamera, db: Session):
    try:
        cam = Camera(cam_name = data.cam_name,
                             location=data.location, 
                             source=data.source)
        db.add(cam)
        db.commit()
        db.refresh(cam)
        return cam
    except Exception as ex:
        db.rollback()
        print("Error encountered when trying to insert camera: ", ex)
        return None

def queryUpdateCameraTask(data: UpdateCameraTask, db:Session):
    try:
        cam = db.query(Camera).filter_by(id=data.id).first()
        if cam:
            cam.task = data.task
            db.commit()

        else:
            raise Exception(f"camera not found with id: {data.id}")
        db.refresh(cam)
        return cam
    except Exception as ex:
        db.rollback()
        print("Error encountered when update camera task: ",ex)
        return None

def queryUpdateCameraBoundary(data: UpdateCameraBorder, db:Session):
    try:
        cam = db.query(Camera).filter_by(id=data.id).first()
        if cam:
            cam.boundary = data.boundary
            db.commit()
        else:
            raise Exception(f"camera not found with id: {data.id}")
        db.refresh(cam)
        return cam
    except Exception as ex:
        db.rollback()
        print("Error encountered when update camera boundary: ",ex)
        return None

def queryRemoveCamera(id:int, db:Session):
    try:
        cam = db.query(Camera).filter_by(id=id).first()
        if cam:
            db.delete(cam)
            db.commit()
        else:
            raise Exception(f"camera not found with id: {id}")
        return cam 
    except Exception as ex:
        db.rollback()
        print("Error encountered when removing camera: ",ex)
        return None
