from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AIModel(Base):
    __tablename__ = "aimodel"

    id = Column(String, primary_key=True, index=True)
    comment = Column(String, nullable=False)
    is_activated_aimodel = Column(Boolean, default=False, nullable=False)
    model_folder_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
