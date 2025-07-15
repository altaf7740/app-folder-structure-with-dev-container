from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import os, uuid, shutil
from typing import List

from .models import FolderEntry
from .schemas import FolderOut
from .database import get_db, init_db
from sqlalchemy.orm import Session

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

init_db()

@app.post("/upload", response_model=FolderOut)
async def upload_folder(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    name = form["name"]
    age = int(form["age"])
    files = form.getlist("folder")

    folder_id = str(uuid.uuid4())
    folder_path = os.path.join(UPLOAD_DIR, folder_id)
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        path = os.path.join(folder_path, file.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(await file.read())

    entry = FolderEntry(name=name, age=age, folder_path=folder_path)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@app.get("/folder-list", response_model=List[FolderOut])
def list_folders(db: Session = Depends(get_db)):
    return db.query(FolderEntry).all()

@app.get("/folder-list/{folder_id}", response_model=FolderOut)
def get_folder(folder_id: int, db: Session = Depends(get_db)):
    entry = db.query(FolderEntry).filter(FolderEntry.id == folder_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Folder not found")
    return entry

@app.put("/folder-list/{folder_id}", response_model=FolderOut)
async def update_folder(
    folder_id: int,
    name: str = Form(...),
    age: int = Form(...),
    db: Session = Depends(get_db)
):
    entry = db.query(FolderEntry).filter(FolderEntry.id == folder_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Folder not found")
    entry.name = name
    entry.age = age
    db.commit()
    db.refresh(entry)
    return entry

@app.delete("/folder-list/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    entry = db.query(FolderEntry).filter(FolderEntry.id == folder_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Folder not found")
    if os.path.exists(entry.folder_path):
        shutil.rmtree(entry.folder_path)
    db.delete(entry)
    db.commit()
    return {"status": "deleted"}
