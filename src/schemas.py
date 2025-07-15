from pydantic import BaseModel
from datetime import datetime

class AIModelBase(BaseModel):
    comment: str
    is_activated_aimodel: bool

class AIModelCreate(AIModelBase):
    pass

class AIModelUpdate(AIModelBase):
    pass

class AIModelOut(AIModelBase):
    id: str
    model_folder_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
