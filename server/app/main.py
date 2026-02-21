from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers import (
    assignment,
    auth,
    chat,
    event,
    group,
    message,
    schedule,
    user,
)

# Database init
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registering routes
app.include_router(auth.auth_router, prefix="/api", tags=["Authentification"])
app.include_router(user.user_router, prefix="/api", tags=["Users"])
app.include_router(assignment.assignment_router, prefix="/api", tags=["Assignments"])
app.include_router(schedule.schedule_router, prefix="/api", tags=["Schedules"])
app.include_router(group.group_router, prefix="/api", tags=["Groups"])
app.include_router(event.events_router, prefix="/api", tags=["Events"])
app.include_router(message.message_router, prefix="/api", tags=["Messages"])
app.include_router(chat.ws_router)

@app.get("/")
def read_root():
    return {"message": "UniConnect API is running"}
