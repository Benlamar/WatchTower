from fastapi import APIRouter, Depends, HTTPException
from schemas.camera import CreateCamera, CamerasInDB
from core.camera import getAllCamera, createCamera
from core.auth import oauth2_scheme, verifyAccessToken, token_exception
from sqlalchemy.orm import Session
from db.database import getDB

router = APIRouter()

@router.get("/")
def camera(db: Session = Depends(getDB), token = Depends(oauth2_scheme)):
    verify_token = verifyAccessToken(token)

    if not verify_token:
        raise token_exception
    
    raw_data = getAllCamera(db)
    if raw_data is not None:
        res = [CamerasInDB(id=data.id, cam_name=data.cam_name, location=data.location, ip_address=data.ip_address) for data in raw_data]
    return res

@router.post("/add")
def addCamera(camera: CreateCamera, db: Session = Depends(getDB), token = Depends(oauth2_scheme)):
    verify_token = verifyAccessToken(token)

    if not verify_token:
        raise token_exception
    
    res = createCamera(camera, db)
    
    if res is None:
        raise HTTPException(detail="Invalid could not create", status_code=400)
    return res
