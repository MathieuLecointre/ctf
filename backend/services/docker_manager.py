import asyncio
import logging
from typing import Any, Dict, Optional
import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)


class DockerManagerError(Exception):
    """Exception de base pour les erreurs de gestion des instances Docker."""
    pass


class InstanceCreationError(DockerManagerError):
    """Levee lorsqu'un conteneur ne peut pas etre instancie."""
    pass


class InstanceNotFoundError(DockerManagerError):
    """Levee lorsqu'une instance n'existe pas sur l'hote Docker."""
    pass


class DockerManager:
    """
    Gestionnaire unifie du cycle de vie des conteneurs CTF.
    Supporte deux modes de fonctionnement :
    1. 'remote' (Architecture 2 VMs UPJV) : Appel mTLS securise vers l'Orchestrateur sur VM 2.
    2. 'local'  (Environnement de dev)   : Utilisation directe de docker-py via socket local.
    """

    def __init__(self):
        self.mode = settings.ORCHESTRATOR_MODE
        self._docker_client = None

    def _get_local_docker_client(self):
        """Initialise le client docker-py pour le mode local."""
        if self._docker_client is None:
            try:
                import docker
                self._docker_client = docker.DockerClient(base_url=settings.DOCKER_HOST)
                self._docker_client.ping()
            except Exception as e:
                logger.error(f"Impossible de se connecter au démon Docker local : {e}")
                raise DockerManagerError(f"Connexion Docker locale echouee: {e}")
        return self._docker_client

    def _get_mtls_client(self) -> httpx.AsyncClient:
        """
        Configure un client HTTPX avec mTLS pour communiquer avec la VM 2.
        Valide avec les fichiers fournis par Hamza (ca.crt, client.crt, client.key).
        """
        cert = None
        if settings.ORCHESTRATOR_CLIENT_CERT and settings.ORCHESTRATOR_CLIENT_KEY:
            cert = (settings.ORCHESTRATOR_CLIENT_CERT, settings.ORCHESTRATOR_CLIENT_KEY)

        verify = settings.ORCHESTRATOR_CA_CERT if settings.ORCHESTRATOR_CA_CERT else False

        headers = {}
        if settings.ORCHESTRATOR_API_KEY:
            headers["X-Orchestrator-Key"] = settings.ORCHESTRATOR_API_KEY

        return httpx.AsyncClient(
            base_url=settings.ORCHESTRATOR_URL,
            verify=verify,
            cert=cert,
            headers=headers,
            timeout=15.0
        )

    async def start_instance(
        self,
        id_utilisateur: int,
        id_challenge: int,
        image_docker: str,
        id_instance_temp: int = 0
    ) -> Dict[str, Any]:
        """
        Demarre un conteneur isole pour un joueur.
        Retourne un dictionnaire contenant container_id, url_cible, et metadonnees.
        """
        if self.mode == "remote":
            return await self._start_remote_instance(id_utilisateur, id_challenge, image_docker)
        else:
            return await self._start_local_instance(id_utilisateur, id_challenge, image_docker, id_instance_temp)

    async def _start_remote_instance(
        self,
        id_utilisateur: int,
        id_challenge: int,
        image_docker: str
    ) -> Dict[str, Any]:
        """Envoie l'ordre d'instanciation a la VM 2 via mTLS."""
        payload = {
            "id_utilisateur": id_utilisateur,
            "id_challenge": id_challenge,
            "image_docker": image_docker,
        }
        try:
            async with self._get_mtls_client() as client:
                response = await client.post("/instances/start", json=payload)
                if response.status_code != 200:
                    raise InstanceCreationError(
                        f"Erreur orchestrateur distant ({response.status_code}): {response.text}"
                    )
                return response.json()
        except httpx.RequestError as exc:
            logger.error(f"Echec de communication mTLS avec VM 2 : {exc}")
            raise InstanceCreationError(f"Orchestrateur distant inaccessible: {exc}")

    async def _start_local_instance(
        self,
        id_utilisateur: int,
        id_challenge: int,
        image_docker: str,
        id_instance: int
    ) -> Dict[str, Any]:
        """Cree le conteneur localement via docker-py (mode developpement)."""
        loop = asyncio.get_running_loop()

        def _blocking_create():
            client = self._get_local_docker_client()
            container_name = f"chal_u{id_utilisateur}_c{id_challenge}"
            network_name = f"{settings.DOCKER_NETWORK_PREFIX}_{id_utilisateur}"

            # 1. Verification / Creation du reseau isole pour ce joueur
            try:
                network = client.networks.get(network_name)
            except Exception:
                network = client.networks.create(
                    network_name,
                    driver="bridge",
                    labels={"ctf.player": str(id_utilisateur)}
                )

            # 2. Nettoyage prealable si un conteneur existe deja sous ce nom
            try:
                old = client.containers.get(container_name)
                old.remove(force=True)
            except Exception:
                pass

            # 3. Construction des labels Traefik et nom d'hote
            host_rule = f"{id_instance}.{settings.INSTANCE_BASE_DOMAIN}" if id_instance else f"chal-{id_utilisateur}-{id_challenge}.{settings.INSTANCE_BASE_DOMAIN}"
            labels = {
                "traefik.enable": "true",
                f"traefik.http.routers.{container_name}.rule": f"Host(`{host_rule}`)",
                f"traefik.http.routers.{container_name}.entrypoints": "web",
                f"traefik.http.services.{container_name}.loadbalancer.server.port": "80",
                "ctf.player_id": str(id_utilisateur),
                "ctf.challenge_id": str(id_challenge),
            }

            # 4. Lancement avec limitations de ressources et isolation
            container = client.containers.run(
                image_docker,
                name=container_name,
                detach=True,
                network=network_name,
                labels=labels,
                mem_limit=settings.INSTANCE_MEM_LIMIT,
                nano_cpus=int(float(settings.INSTANCE_CPU_LIMIT) * 1e9),
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                restart_policy={"Name": "no"},
            )

            url_cible = f"http://{host_rule}"
            return {
                "container_id": container.id,
                "url_cible": url_cible,
                "status": "running"
            }

        try:
            return await loop.run_in_executor(None, _blocking_create)
        except Exception as e:
            logger.error(f"Erreur lors de la creation locale du conteneur : {e}")
            raise InstanceCreationError(f"Echec de creation du conteneur: {e}")

    async def stop_instance(self, container_id: str) -> bool:
        """Detruit un conteneur actif."""
        if self.mode == "remote":
            try:
                async with self._get_mtls_client() as client:
                    response = await client.delete(f"/instances/{container_id}")
                    return response.status_code in [200, 204]
            except Exception as e:
                logger.error(f"Erreur lors de l'arret distant de {container_id}: {e}")
                return False
        else:
            loop = asyncio.get_running_loop()

            def _blocking_stop():
                try:
                    client = self._get_local_docker_client()
                    container = client.containers.get(container_id)
                    container.remove(force=True)
                    return True
                except Exception as e:
                    logger.warning(f"Conteneur {container_id} introuvable ou deja supprime : {e}")
                    return False

            return await loop.run_in_executor(None, _blocking_stop)

    async def restart_instance(
        self,
        container_id: str,
        id_utilisateur: int,
        id_challenge: int,
        image_docker: str,
        id_instance: int = 0
    ) -> Dict[str, Any]:
        """Reinitialise l'instance (Crash du joueur) : Delete + Recreate."""
        await self.stop_instance(container_id)
        return await self.start_instance(id_utilisateur, id_challenge, image_docker, id_instance)


# Instance unique (Singleton) du DockerManager
docker_manager = DockerManager()
