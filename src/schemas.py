from pydantic import BaseModel

class FolderBase(BaseModel):
    name: str
    age: int

class FolderCreate(FolderBase):
    pass

class FolderUpdate(FolderBase):
    pass

class FolderOut(FolderBase):
    id: int
    folder_path: str

    class Config:
        orm_mode = True
