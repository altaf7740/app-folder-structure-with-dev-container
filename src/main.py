from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import NoResultFound

import os
import uuid
os.makedirs("uploads", exist_ok=True)  # <-- ADD THIS LINE BEFORE FastAPI init

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

engine = create_engine("sqlite:///./folders.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class FolderEntry(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    folder_path = Column(String)

Base.metadata.create_all(bind=engine)

@app.post("/upload")
async def upload_folder(request: Request):
    form = await request.form()
    name = form["name"]
    age = int(form["age"])
    files = form.getlist("folder")

    folder_id = str(uuid.uuid4())
    folder_path = os.path.join("uploads", folder_id)
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        rel_path = file.filename
        file_path = os.path.join(folder_path, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())

    db = Session()
    entry = FolderEntry(name=name, age=age, folder_path=folder_path)
    db.add(entry)
    db.commit()
    return JSONResponse({"status": "success", "folder_id": folder_id})

@app.get("/folder-list")
def get_all_folders():
    db = Session()
    folders = db.query(FolderEntry).all()
    return [{"id": f.id, "name": f.name, "age": f.age, "folder_path": f.folder_path} for f in folders]

@app.get("/folder-list/{folder_id}")
def get_folder(folder_id: int):
    db = Session()
    folder = db.query(FolderEntry).filter(FolderEntry.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"id": folder.id, "name": folder.name, "age": folder.age, "folder_path": folder.folder_path}

@app.put("/folder-list/{folder_id}")
async def update_folder(folder_id: int, name: str = Form(...), age: int = Form(...)):
    db = Session()
    folder = db.query(FolderEntry).filter(FolderEntry.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder.name = name
    folder.age = age
    db.commit()
    return {"status": "updated"}

@app.delete("/folder-list/{folder_id}")
def delete_folder(folder_id: int):
    db = Session()
    folder = db.query(FolderEntry).filter(FolderEntry.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    if os.path.exists(folder.folder_path):
        for root, dirs, files in os.walk(folder.folder_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(folder.folder_path)
    db.delete(folder)
    db.commit()
    return {"status": "deleted"}
