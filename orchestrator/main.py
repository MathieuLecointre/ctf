import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel, Field

from orchestrator.config import settings
from orchestrator.service import orchestrator_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ctf.orchestrator")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agent d'orchestration dynamique Docker sur VM 2 - CTF BUT5",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None
)


# ==============================================================================
# Schemas des requetes / reponses
# ==============================================================================

class StartInstanceRequest(BaseModel):
    id_utilisateur: int = Field(..., gt=0, examples=[1])
    id_challenge: int = Field(..., gt=0, examples=[42])
    image_docker: str = Field(..., examples=["ctf/web-sqli:1.0"])


class InstanceActionResponse(BaseModel):
    status: str
    container_id: str
    container_name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    target_url: Optional[str] = None
    runtime: Optional[str] = None


# ==============================================================================
# Middleware de securite optionnel (Cle secrete d'API)
# ==============================================================================

async def verify_orchestrator_auth(x_orchestrator_key: Optional[str] = Header(None)):
    """Verifie la cle d'API secrete si elle est configuree en defense en profondeur."""
    if settings.API_SECRET_KEY and x_orchestrator_key != settings.API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cle secrete d'orchestration invalide"
        )


# ==============================================================================
# Endpoints
# ==============================================================================

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Sanite de l'orchestrateur VM 2."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "docker_connected": orchestrator_service.client is not None,
        "runtime": settings.DOCKER_RUNTIME
    }


@app.post(
    "/instances/start",
    response_model=InstanceActionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Instances"]
)
async def start_instance(
    req: StartInstanceRequest,
    _auth: None = Header(None)
):
    """
    Cree et demarre une instance de challenge isolee pour un joueur sur la VM 2.
    """
    try:
        result = await orchestrator_service.start_challenge_instance(
            id_utilisateur=req.id_utilisateur,
            id_challenge=req.id_challenge,
            image_docker=req.image_docker
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Echec creation instance : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur orchestration Docker : {e}"
        )


@app.delete(
    "/instances/{container_id}",
    status_code=status.HTTP_200_OK,
    tags=["Instances"]
)
async def stop_instance(container_id: str):
    """
    Detruit un conteneur actif et libere le port et les ressources.
    """
    success = await orchestrator_service.stop_challenge_instance(container_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conteneur introuvable ou deja supprime"
        )
    return {"status": "stopped", "container_id": container_id}


@app.get(
    "/instances/{container_id}/status",
    tags=["Instances"]
)
async def get_status(container_id: str):
    """
    Verifie si le conteneur est toujours en vie.
    """
    status_str = await orchestrator_service.get_instance_status(container_id)
    if status_str is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conteneur introuvable"
        )
    return {"container_id": container_id, "status": status_str}
