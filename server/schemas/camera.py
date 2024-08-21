from pydantic import BaseModel

class CameraBase(BaseModel):
    cam_name : str
    location : str
    source : str

class CreateCamera(CameraBase):
    pass

class DeleteCamera(BaseModel):
    id: int

class CamerasInDB(CameraBase):
    id : int

class UpdateCameraTask(BaseModel):
    id: int
    task: str

class UpdateCameraBorder(BaseModel):
    id: int
    boundary: str

class CameraError(BaseModel):
    status: int
    message: str
