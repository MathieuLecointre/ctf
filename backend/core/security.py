from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import re
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings

# Contexte de hachage de mot de passe base sur bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Roles du systeme (RBAC)
ROLE_JOUEUR = "joueur"
ROLE_ADMIN = "admin"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifie si un mot de passe en clair correspond au hash enregistre."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genere le hash securise d'un mot de passe."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    role: str = ROLE_JOUEUR,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Genere un token JWT encode contenant l'identifiant utilisateur (sub) et son role.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode et valide la signature et l'expiration d'un token JWT.
    Retourne le payload s'il est valide, sinon None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def is_valid_flag_format(flag: str) -> bool:
    """
    Verifie que la chaine soumise respecte le format standard CTF{...}.
    Permet de filtrer en amont avant toute requete couteuse en base de donnees.
    """
    if not flag:
        return False
    return bool(re.match(settings.FLAG_REGEX, flag.strip()))
