from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os, uuid, shutil

from .models import AIModel
from .schemas import AIModelCreate, AIModelUpdate, AIModelOut
from .database import init_db, get_db

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

init_db()

@app.post("/aimodels", response_model=AIModelOut)
async def upload_aimodel(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    comment = form["comment"]
    is_activated = form.get("is_activated_aimodel", "false").lower() == "true"
    files = form.getlist("folder")

    if is_activated:
        db.query(AIModel).filter(AIModel.is_activated_aimodel == True).update(
            {AIModel.is_activated_aimodel: False}
        )

    model_id = str(uuid.uuid4())
    folder_path = os.path.join(UPLOAD_DIR, model_id)
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        path = os.path.join(folder_path, file.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(await file.read())

    entry = AIModel(
        id=model_id,
        comment=comment,
        is_activated_aimodel=is_activated,
        model_folder_path=folder_path
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.put("/aimodels/{model_id}", response_model=AIModelOut)
async def update_aimodel(
    model_id: str,
    comment: str = Form(...),
    is_activated_aimodel: bool = Form(...),
    db: Session = Depends(get_db)
):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if is_activated_aimodel:
        db.query(AIModel).filter(AIModel.is_activated_aimodel == True).update(
            {AIModel.is_activated_aimodel: False}
        )

    model.comment = comment
    model.is_activated_aimodel = is_activated_aimodel
    db.commit()
    db.refresh(model)
    return model


@app.get("/aimodels/active", response_model=AIModelOut)
def get_active_model(db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.is_activated_aimodel == True).first()
    if not model:
        raise HTTPException(status_code=404, detail="No active model found")
    return model


@app.get("/aimodels", response_model=List[AIModelOut])
def list_aimodels(db: Session = Depends(get_db)):
    return db.query(AIModel).all()

@app.get("/aimodels/{model_id}", response_model=AIModelOut)
def get_aimodel(model_id: str, db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@app.delete("/aimodels/{model_id}")
def delete_aimodel(model_id: str, db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if os.path.exists(model.model_folder_path):
        shutil.rmtree(model.model_folder_path)
    db.delete(model)
    db.commit()
    return {"status": "deleted"}
