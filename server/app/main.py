from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers import assignment, users

# Database init
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registering routes
app.include_router(users.user_router, prefix="/api", tags=["Users"])
app.include_router(assignment.assignment_router, prefix="/api", tags=["Assignments"])

@app.get("/")
def read_root():
    return {"message": "UniConnect API is running"}
