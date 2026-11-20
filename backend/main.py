import asyncio
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.api import routes_auth
from backend.core.config import settings
from backend.core.database import Base, engine
from backend.services.websocket_mgr import scoreboard_ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ctf.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire du cycle de vie de l'application FastAPI.
    """
    logger.info("Demarrage de l'API CTF Platform...")
    yield
    logger.info("Arret de l'API CTF Platform...")
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API Backend de la Plateforme CTF Self-Hosted - BUT Informatique S5",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour permettre les requetes depuis le Frontend Vue 3
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de verification de l'etat de l'API
@app.get(f"{settings.API_V1_STR}/health", tags=["Monitoring"])
async def health_check():
    """Endpoint de sanite pour Traefik, Docker et Prometheus."""
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "orchestrator_mode": settings.ORCHESTRATOR_MODE
    }


# Inclusion des routes
app.include_router(routes_auth.router, prefix=settings.API_V1_STR)


# WebSocket pour le Scoreboard temps reel
@app.websocket("/ws/scoreboard")
async def websocket_scoreboard_endpoint(websocket: WebSocket):
    """Endpoint WebSocket utilise par le composant Scoreboard du Frontend Vue 3."""
    await scoreboard_ws_manager.connect(websocket)
    try:
        while True:
            # Ecoute les pings/messages eventuels des clients (keep-alive)
            await websocket.receive_text()
    except WebSocketDisconnect:
        scoreboard_ws_manager.disconnect(websocket)
