from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import ROLE_ADMIN, decode_access_token
from backend.models.db_models import Utilisateur

# Schema OAuth2 avec route de login pour la documentation Swagger /docs
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Utilisateur:
    """
    Extrait et valide le token JWT de la requete.
    Recupere l'utilisateur en base de donnees.
    Leve une exception HTTP 401 si le token est invalide ou l'utilisateur introuvable.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou session expiree",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    # Recherche de l'utilisateur en base de donnees
    query = select(Utilisateur).where(Utilisateur.id_utilisateur == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_admin(
    current_user: Utilisateur = Depends(get_current_user)
) -> Utilisateur:
    """
    Verifie que l'utilisateur authentifie dispose des droits administrateur (RBAC).
    Leve une exception HTTP 403 Forbidden dans le cas contraire.
    """
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis pour cette action"
        )
    return current_user
