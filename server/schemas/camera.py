from pydantic import BaseModel

class CameraBase(BaseModel):
    cam_name : str
    location : str
    ip_address : str

class CreateCamera(CameraBase):
    pass

class DeleteCamera(BaseModel):
    id: int

class CamerasInDB(CameraBase):
    id : int
