# main.py
from fastapi import FastAPI

from app.db.database import Base, engine
from app.models import (
    models,
)

# Database init
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "UniConnect API is running"}
