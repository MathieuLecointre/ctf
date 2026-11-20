from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class OrchestratorSettings(BaseSettings):
    # Informations de base
    PROJECT_NAME: str = "CTF Orchestrator Agent (VM 2)"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Reseau & Ports de l'agent
    HOST: str = "0.0.0.0"
    PORT: int = 8443

    # Securite mTLS (fichiers fournis par Hamza)
    SSL_CA_CERT: Optional[str] = "certs/ca.crt"
    SSL_SERVER_CERT: Optional[str] = "certs/server.crt"
    SSL_SERVER_KEY: Optional[str] = "certs/server.key"
    API_SECRET_KEY: Optional[str] = None  # Jeton optionnel en defense en profondeur

    # Configuration Docker sur VM 2
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    DOCKER_RUNTIME: str = "runsc"          # Runtime gVisor (fallback automatique sur runc si absent)
    PLAYER_NET_PREFIX: str = "net_joueur"  # Prefixe des reseaux isoles (ex: net_joueur1)
    SUBNET_BASE: str = "172.30"            # Plage 172.30.X.0/24 par joueur (conforme schema Hamza)

    # Plage de ports dynamiques alloues aux challenges
    PORT_RANGE_START: int = 31001
    PORT_RANGE_END: int = 31999
    VM2_WIREGUARD_IP: str = "10.10.10.2"

    # Limitations de ressources conteneurs
    CONTAINER_MEM_LIMIT: str = "256m"
    CONTAINER_CPU_LIMIT: str = "0.5"

    # Whitelist des images autorisees (Securite anti-arbitrary container execution)
    ALLOWED_IMAGE_PREFIXES: List[str] = ["ctf/", "challenges/"]

    model_config = SettingsConfigDict(
        env_file=".env.orchestrator",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = OrchestratorSettings()
