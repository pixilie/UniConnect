from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers import admin, assignment, group, schedule, user

# Database init
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registering routes
app.include_router(user.user_router, prefix="/api", tags=["Users"])
app.include_router(assignment.assignment_router, prefix="/api", tags=["Assignments"])
app.include_router(schedule.schedule_router, prefix="/api", tags=["Schedules"])
app.include_router(admin.admin_router, prefix="/api", tags=["Administrator"])
app.include_router(group.group_router, prefix="/api", tags=["Groups"])

@app.get("/")
def read_root():
    return {"message": "UniConnect API is running"}
