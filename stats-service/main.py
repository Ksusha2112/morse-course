import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("STATS_DB_PATH", "sqlite:///./stats.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GlobalStats(Base):
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True, index=True)
    encodes = Column(Integer, default=0)
    decodes = Column(Integer, default=0)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stats Service")


class StatsUpdate(BaseModel):
    direction: str


def get_or_create_stats(db) -> GlobalStats:
    stats = db.query(GlobalStats).first()
    if stats is None:
        stats = GlobalStats(encodes=0, decodes=0)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats


@app.get("/health")
def health():
    return {"status": "ok", "service": "stats"}


@app.post("/api/increment")
def increment_stat(data: StatsUpdate):
    if data.direction not in ("encode", "decode"):
        raise HTTPException(status_code=400, detail="Неизвестное направление")
    db = SessionLocal()
    try:
        stats = get_or_create_stats(db)
        if data.direction == "encode":
            stats.encodes += 1
        else:
            stats.decodes += 1
        db.commit()
    finally:
        db.close()
    return {"status": "ok"}


@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    try:
        stats = get_or_create_stats(db)
        return {
            "encodes": stats.encodes,
            "decodes": stats.decodes,
            "total": stats.encodes + stats.decodes,
        }
    finally:
        db.close()
