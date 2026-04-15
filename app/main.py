import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import routers
from app.services import deactivate_expired_polls

from .db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background tasks...")
    task = asyncio.create_task(deactivate_expired_polls())
    yield
    print("Shutting down background tasks...")
    task.cancel()


Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan, title="UniConnect API")

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
