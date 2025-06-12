from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import json

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# --- Logging Setup ---
os.makedirs("logs", exist_ok=True)

# Log filename with today's date
log_filename = datetime.now().strftime("logs/api_%Y-%m-%d.log")

# Timed Rotating Handler: creates new file daily, keeps 7 days
file_handler = TimedRotatingFileHandler(
    filename=log_filename,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
    utc=True,
)

file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Console handler for terminal output
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)

# Apply both handlers to root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI()

# --- CORS (if GUI is running separately) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SQLAlchemy Setup ---
DATABASE_URL = "sqlite:///./villas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# --- ORM Model ---
class VillaORM(Base):
    __tablename__ = "villas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    details = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    sqft = Column(Integer, nullable=False)
    occupancy = Column(Integer, nullable=False)
    imageUrl = Column(String, nullable=False)
    amenity = Column(String, nullable=False)
    createdDate = Column(DateTime, default=datetime.now(timezone.utc))
    updatedDate = Column(DateTime, default=datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)


# --- Pydantic Schemas ---
class VillaBase(BaseModel):
    name: str
    details: str
    rate: float
    sqft: int
    occupancy: int
    imageUrl: str
    amenity: str


class Villa(VillaBase):
    id: int
    createdDate: datetime
    updatedDate: datetime

    class Config:
        orm_mode = True


# --- API Routes ---
@app.get("/api/VillaAPI", response_model=List[Villa])
def get_all_villas():
    with SessionLocal() as db:
        villas = db.query(VillaORM).all()
        logger.info(f"Retrieved {len(villas)} villas.")
        return villas


@app.get("/api/VillaAPI/{villa_id}", response_model=Villa)
def get_villa(villa_id: int = Path(...)):
    with SessionLocal() as db:
        villa = db.query(VillaORM).get(villa_id)
        if not villa:
            logger.warning(f"Villa with ID {villa_id} not found.")
            raise HTTPException(status_code=404, detail="Villa not found")
        logger.info(f"Retrieved villa with ID {villa_id}")
        return villa


@app.post("/api/VillaAPI", status_code=201)
def create_villa(villa: VillaBase):
    with SessionLocal() as db:
        new_villa = VillaORM(
            **villa.dict(),
            createdDate=datetime.now(timezone.utc),
            updatedDate=datetime.now(timezone.utc),
        )
        db.add(new_villa)
        db.commit()
        logger.info(f"Created villa: {villa.name}")
        return {"message": "Villa created successfully"}


@app.put("/api/VillaAPI/{villa_id}", status_code=204)
def update_villa(villa_id: int, villa: VillaBase):
    with SessionLocal() as db:
        db_villa = db.query(VillaORM).get(villa_id)
        if not db_villa:
            logger.warning(f"Update failed. Villa with ID {villa_id} not found.")
            raise HTTPException(status_code=404, detail="Villa not found")

        for key, value in villa.dict().items():
            setattr(db_villa, key, value)
        db_villa.updatedDate = datetime.utcnow()
        db.commit()
        logger.info(f"Updated villa ID {villa_id}")


@app.patch("/api/VillaAPI/{villa_id}", status_code=204)
def patch_villa(villa_id: int, updates: List[dict]):
    with SessionLocal() as db:
        db_villa = db.query(VillaORM).get(villa_id)
        if not db_villa:
            logger.warning(f"Patch failed. Villa with ID {villa_id} not found.")
            raise HTTPException(status_code=404, detail="Villa not found")

        for update in updates:
            if update.get("op") == "replace":
                path = update.get("path", "").lstrip("/")
                value = update.get("value")
                if hasattr(db_villa, path):
                    setattr(db_villa, path, value)
                    logger.info(f"Patched villa ID {villa_id}: set {path} = {value}")

        db_villa.updatedDate = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Completed patch for villa ID {villa_id}")


@app.delete("/api/VillaAPI/{villa_id}", status_code=204)
def delete_villa(villa_id: int):
    with SessionLocal() as db:
        villa = db.query(VillaORM).get(villa_id)
        if not villa:
            logger.warning(f"Delete failed. Villa with ID {villa_id} not found.")
            raise HTTPException(status_code=404, detail="Villa not found")
        db.delete(villa)
        db.commit()
        logger.info(f"Deleted villa with ID {villa_id}")
