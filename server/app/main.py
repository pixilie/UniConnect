from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers import users

# Database init
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registering routes
app.include_router(users.user_router, prefix="/api", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "UniConnect API is running", "code": 200}
