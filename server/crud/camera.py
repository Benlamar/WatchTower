from sqlalchemy.orm import Session
from db.models import camera
from schemas.camera import CreateCamera

def queryAllCamera(db: Session):
    try:
        return db.query(camera.Camera).all()
    except:
        print("Error encountered when tyrying to getAllUsers in curd")
        return []
    
def queryInsertCamera(data: CreateCamera, db: Session):
    print("Data to insert : ", data)
    try:
        cam = camera.Camera(cam_name = data.cam_name,
                             location=data.location, 
                             ip_address=data.ip_address)
        db.add(cam)
        db.commit()
        db.refresh(cam)
        return cam
    except Exception as ex:
        db.rollback()
        print("Error encountered when trying to insert camera: "+ex)
        return None
