from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.core.security import (
    ROLE_JOUEUR,
    create_access_token,
    get_password_hash,
    verify_password,
)
from backend.models.db_models import Challenge, Soumission, Utilisateur
from backend.models.schemas import Token, UserCreate, UserLogin, UserResponse, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouveau joueur"
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Cree un nouveau compte joueur :
    - Verifie l'unicite du pseudo et de l'adresse email (409 Conflict si doublon).
    - Hache le mot de passe de maniere securisee avec bcrypt.
    - Assigne le role 'joueur' par defaut.
    """
    # Verifier si l'email existe deja
    query_email = select(Utilisateur).where(Utilisateur.email == user_in.email)
    existing_email = (await db.execute(query_email)).scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse email est déjà enregistrée."
        )

    # Verifier si le pseudo existe deja
    query_pseudo = select(Utilisateur).where(Utilisateur.pseudo == user_in.pseudo)
    existing_pseudo = (await db.execute(query_pseudo)).scalar_one_or_none()
    if existing_pseudo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce pseudo est déjà utilisé."
        )

    # Creation du compte
    db_user = Utilisateur(
        pseudo=user_in.pseudo.strip(),
        email=user_in.email.strip().lower(),
        mot_de_passe_hash=get_password_hash(user_in.mot_de_passe),
        role=ROLE_JOUEUR,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponse(
        id_utilisateur=db_user.id_utilisateur,
        pseudo=db_user.pseudo,
        email=db_user.email,
        role=db_user.role,
        date_inscription=db_user.date_inscription or datetime.now(timezone.utc),
        score=0
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Connexion et generation de token JWT (format JSON)"
)
async def login_json(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Authentifie un joueur ou un administrateur via son email et mot de passe.
    Retourne un token JWT Bearer valide contenant l'identifiant et le role.
    """
    query = select(Utilisateur).where(Utilisateur.email == credentials.email.strip().lower())
    user = (await db.execute(query)).scalar_one_or_none()

    if not user or not verify_password(credentials.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id_utilisateur,
        role=user.role
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        id_utilisateur=user.id_utilisateur,
        pseudo=user.pseudo
    )


@router.post(
    "/login/oauth",
    response_model=Token,
    include_in_schema=True,
    summary="Connexion via formulaire OAuth2 (pour Swagger UI /docs)"
)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Endpoint de connexion compatible avec le bouton 'Authorize' de Swagger UI.
    Le champ 'username' accepte soit l'email, soit le pseudo.
    """
    identifier = form_data.username.strip().lower()
    query = select(Utilisateur).where(
        (Utilisateur.email == identifier) | (Utilisateur.pseudo == form_data.username.strip())
    )
    user = (await db.execute(query)).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id_utilisateur,
        role=user.role
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        id_utilisateur=user.id_utilisateur,
        pseudo=user.pseudo
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Profil de l'utilisateur connecte"
)
async def read_current_user_profile(
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retourne les informations du profil utilisateur ainsi que son score calcule
    a partir des defis resolus de maniere unique.
    """
    # Calcul du score : somme des points des challenges resolus avec succes (distincts)
    query_score = (
        select(func.coalesce(func.sum(Challenge.points), 0))
        .select_from(Soumission)
        .join(Challenge, Soumission.id_challenge == Challenge.id_challenge)
        .where(
            Soumission.id_utilisateur == current_user.id_utilisateur,
            Soumission.est_valide == True
        )
    )
    score_result = await db.execute(query_score)
    user_score = score_result.scalar() or 0

    return UserResponse(
        id_utilisateur=current_user.id_utilisateur,
        pseudo=current_user.pseudo,
        email=current_user.email,
        role=current_user.role,
        date_inscription=current_user.date_inscription,
        score=user_score
    )
