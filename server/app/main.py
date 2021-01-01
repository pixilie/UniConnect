from fastapi import FastAPI

from app import routers
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(routers.auth_router, prefix="/api", tags=["Authentification"])
app.include_router(routers.user_router, prefix="/api", tags=["Users"])
app.include_router(routers.assignment_router, prefix="/api", tags=["Assignments"])
app.include_router(routers.group_router, prefix="/api", tags=["Groups"])
app.include_router(routers.events_router, prefix="/api", tags=["Events"])
app.include_router(routers.resource_router, prefix="/api", tags=["Resources"])
app.include_router(routers.schedule_router, prefix="/api", tags=["Schedules"])
app.include_router(routers.poll_router, prefix="/api", tags=["Polls"])
app.include_router(routers.ws_router)

@app.get("/")
def read_root():
    return {"message": "UniConnect API is running"}
