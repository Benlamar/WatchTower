from fastapi import APIRouter, Depends, HTTPException
from schemas.camera import CreateCamera, CamerasInDB, DeleteCamera, UpdateCameraBorder
from core.camera import getAllCamera, createCamera, removeCamera, updateCameraBoundary
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
        res = [CamerasInDB(id=data.id, cam_name=data.cam_name, location=data.location, source=data.source) for data in raw_data]
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

@router.delete("/remove/{cam_id}")
def deleteCamera(cam_id: int, db: Session = Depends(getDB), token = Depends(oauth2_scheme)):
    verify_token = verifyAccessToken(token)
    if not verify_token:
        raise token_exception
    
    res = removeCamera(cam_id, db)
    if res is None:
        raise HTTPException(detail="Invalid could not remove camera", status_code=400)
    return res

@router.post("/boundary")
def setBorder(border: UpdateCameraBorder, db: Session = Depends(getDB), token = Depends(oauth2_scheme)):
    verify_token = verifyAccessToken(token)
    if not verify_token:
        raise token_exception
    res = updateCameraBoundary(border, db)
    return res