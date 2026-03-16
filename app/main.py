from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import routers
from app.db.database import get_db

from .db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, on autorise tout le monde ("*")
    allow_credentials=True,
    allow_methods=["*"],  # Autorise GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],  # Autorise tous les en-têtes
)

app.include_router(routers.auth_router, prefix="/api", tags=["Authentification"])
app.include_router(routers.user_router, prefix="/api", tags=["Users"])
app.include_router(routers.assignment_router, prefix="/api", tags=["Assignments"])
app.include_router(routers.group_router, prefix="/api", tags=["Groups"])
app.include_router(routers.events_router, prefix="/api", tags=["Events"])
app.include_router(routers.resource_router, prefix="/api", tags=["Resources"])
app.include_router(routers.schedule_router, prefix="/api", tags=["Schedules"])
app.include_router(routers.poll_router, prefix="/api", tags=["Polls"])
app.include_router(routers.announcement_router, prefix="/api", tags=["Announcements"])
app.include_router(routers.ws_router, prefix="/ws", tags=["Websockets"])

app.mount("/styles", StaticFiles(directory="client/styles"), name="styles")
app.mount("/scripts", StaticFiles(directory="client/scripts"), name="scripts")
app.mount("/assets", StaticFiles(directory="client/assets"), name="assets")

@app.get("/")
def read_root():
    return RedirectResponse(url="/home.html")

@app.get("/favicon.ico")
def get_favicon():
    return FileResponse("client/assets/favicon.ico")

app.mount("/", StaticFiles(directory="client/pages", html=True), name="pages")
