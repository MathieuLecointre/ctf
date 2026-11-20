from datetime import datetime
from typing import Annotated, List, Optional
from pydantic import BaseModel, ConfigDict, Field

# Format d'email tolerant pour les domaines internes/locaux (ex: ctf.local, u-picardie.fr)
EmailField = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        examples=["joueur@ctf.local", "etudiant@u-picardie.fr"],
    ),
]


# ==============================================================================
# Schemas UTILISATEUR & AUTHENTIFICATION
# ==============================================================================

class UserBase(BaseModel):
    pseudo: str = Field(..., min_length=3, max_length=50, examples=["cybershark"])
    email: EmailField


class UserCreate(UserBase):
    mot_de_passe: str = Field(..., min_length=8, max_length=100, examples=["M0tDeP@sseSecurise"])


class UserLogin(BaseModel):
    email: EmailField
    mot_de_passe: str


class UserUpdate(BaseModel):
    pseudo: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    role: Optional[str] = Field(None, pattern=r"^(joueur|admin)$")


class UserResponse(UserBase):
    id_utilisateur: int
    role: str
    date_inscription: datetime
    score: int = 0

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    id_utilisateur: int
    pseudo: str


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: Optional[int] = None


# ==============================================================================
# Schemas CHALLENGE
# ==============================================================================

class ChallengeBase(BaseModel):
    titre: str = Field(..., min_length=3, max_length=100)
    description: str
    categorie: str = Field(..., max_length=50, examples=["Web", "Reseau", "Crypto", "Systeme", "Forensic"])
    difficulte: int = Field(..., ge=1, le=5, description="Niveau de 1 a 5")
    points: int = Field(..., gt=0, examples=[50, 100, 300])


class ChallengeCreate(ChallengeBase):
    flag_attendu: str = Field(..., description="Flag valide au format CTF{...}")
    image_docker: str = Field(..., max_length=150, examples=["ctf/web-sqli:latest"])


class ChallengeUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    difficulte: Optional[int] = Field(None, ge=1, le=5)
    points: Optional[int] = Field(None, gt=0)
    flag_attendu: Optional[str] = None
    image_docker: Optional[str] = None


class ChallengePublic(ChallengeBase):
    """Schema destine aux joueurs (masque le flag et l'image Docker)."""
    id_challenge: int
    est_resolu: bool = False

    model_config = ConfigDict(from_attributes=True)


class ChallengeAdmin(ChallengeBase):
    """Schema complet reserve au back-office administrateur."""
    id_challenge: int
    flag_attendu: str
    image_docker: str

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Schemas INSTANCE DOCKER
# ==============================================================================

class InstanceCreate(BaseModel):
    id_challenge: int


class InstanceResponse(BaseModel):
    id_instance: int
    id_utilisateur: int
    id_challenge: int
    url_cible: str
    date_lancement: datetime
    statut: str
    temps_restant_secondes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Schemas SOUMISSION & VALIDATION DE FLAG
# ==============================================================================

class SoumissionCreate(BaseModel):
    id_challenge: int
    flag_soumis: str = Field(..., min_length=5, max_length=255)


class SoumissionResponse(BaseModel):
    id_soumission: int
    id_challenge: int
    est_valide: bool
    date_soumission: datetime
    message: str
    points_gagnes: int = 0
    est_first_blood: bool = False

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Schemas BADGE & CLASSEMENT (SCOREBOARD)
# ==============================================================================

class BadgeResponse(BaseModel):
    id_badge: int
    nom_badge: str
    seuil_points: int
    debloque: bool = False
    date_obtention: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ScoreboardEntry(BaseModel):
    rang: int
    id_utilisateur: int
    pseudo: str
    score_total: int
    nb_resolutions: int
    dernier_flag_date: Optional[datetime] = None
    badges: List[str] = []

    model_config = ConfigDict(from_attributes=True)
