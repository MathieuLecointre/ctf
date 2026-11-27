import asyncio
import logging
import socket
from typing import Any, Dict, List, Optional
import docker
from docker.errors import DockerException, NotFound

from orchestrator.config import settings

logger = logging.getLogger("orchestrator.service")


class OrchestratorService:
    """
    Service Docker d'execution directe sur la VM 2.
    Gere l'isolation gVisor, les sous-reseaux et les ports dynamiques WireGuard.
    """

    def __init__(self):
        try:
            self.client = docker.DockerClient(base_url=settings.DOCKER_HOST)
            self._available_runtimes = self._detect_runtimes()
        except DockerException as e:
            logger.error(f"Erreur d'initialisation Docker sur VM 2: {e}")
            self.client = None
            self._available_runtimes = []

    def _detect_runtimes(self) -> List[str]:
        """Detecte les runtimes disponibles (gVisor / runsc vs runc)."""
        try:
            info = self.client.info()
            runtimes = info.get("Runtimes", {})
            logger.info(f"Runtimes Docker detectes sur VM 2 : {list(runtimes.keys())}")
            return list(runtimes.keys())
        except Exception:
            return ["runc"]

    def _is_image_allowed(self, image_name: str) -> bool:
        """Controle de securite : verification de la liste blanche d'images."""
        return any(image_name.startswith(prefix) for prefix in settings.ALLOWED_IMAGE_PREFIXES)

    def _find_available_port(self) -> int:
        """Trouve un port libre dans la plage definie (31001-31999)."""
        # 1. Recuperer tous les ports deja occupes par des conteneurs
        used_ports = set()
        for container in self.client.containers.list():
            ports_dict = container.attrs.get("NetworkSettings", {}).get("Ports", {})
            if ports_dict:
                for mappings in ports_dict.values():
                    if mappings:
                        for m in mappings:
                            host_port = m.get("HostPort")
                            if host_port and host_port.isdigit():
                                used_ports.add(int(host_port))

        # 2. Chercher le premier port libre dans la plage
        for port in range(settings.PORT_RANGE_START, settings.PORT_RANGE_END + 1):
            if port not in used_ports:
                # Verification au niveau socket OS
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    if s.connect_ex(("127.0.0.1", port)) != 0:
                        return port

        raise RuntimeError("Aucun port libre disponible dans la plage allouee.")

    def _get_or_create_player_network(self, id_utilisateur: int):
        """
        Cree un bridge Docker isole par joueur (ex: net_joueur1).
        Subnet de type 172.30.X.0/24 conformement au schema reseau.
        """
        network_name = f"{settings.PLAYER_NET_PREFIX}{id_utilisateur}"
        try:
            return self.client.networks.get(network_name)
        except NotFound:
            # Calcul du troisieme octet (modulo 250 + 1) pour eviter les collisions
            subnet_octet = (id_utilisateur % 250) + 1
            ipam_pool = docker.types.IPAMPool(
                subnet=f"{settings.SUBNET_BASE}.{subnet_octet}.0/24",
                gateway=f"{settings.SUBNET_BASE}.{subnet_octet}.1"
            )
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

            logger.info(f"Creation du reseau isole {network_name} ({settings.SUBNET_BASE}.{subnet_octet}.0/24)")
            return self.client.networks.create(
                network_name,
                driver="bridge",
                ipam=ipam_config,
                internal=False,  # Bloque par nftables sur l'hote VM 2
                labels={"ctf.player": str(id_utilisateur)}
            )

    async def start_challenge_instance(
        self,
        id_utilisateur: int,
        id_challenge: int,
        image_docker: str
    ) -> Dict[str, Any]:
        """
        Instancie le conteneur du defi avec gVisor, limites de ressources et port WireGuard.
        """
        if not self._is_image_allowed(image_docker):
            raise ValueError(f"Image '{image_docker}' non autorisee par la politique de securite.")

        loop = asyncio.get_running_loop()

        def _sync_start():
            container_name = f"chal_u{id_utilisateur}_c{id_challenge}"

            # 1. Nettoyage si existant
            try:
                existing = self.client.containers.get(container_name)
                existing.remove(force=True)
            except NotFound:
                pass

            # 2. Reseau joueur
            network = self._get_or_create_player_network(id_utilisateur)

            # 3. Port dynamique pour WireGuard
            allocated_port = self._find_available_port()

            # 4. Selection du runtime securise
            chosen_runtime = settings.DOCKER_RUNTIME if settings.DOCKER_RUNTIME in self._available_runtimes else "runc"

            # 5. Lancement securise du conteneur
            container = self.client.containers.run(
                image=image_docker,
                name=container_name,
                detach=True,
                network=network.name,
                runtime=chosen_runtime,
                ports={"80/tcp": (settings.VM2_WIREGUARD_IP, allocated_port)},
                mem_limit=settings.CONTAINER_MEM_LIMIT,
                nano_cpus=int(float(settings.CONTAINER_CPU_LIMIT) * 1e9),
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                restart_policy={"Name": "no"},
                labels={
                    "ctf.player_id": str(id_utilisateur),
                    "ctf.challenge_id": str(id_challenge),
                    "ctf.allocated_port": str(allocated_port),
                }
            )

            # URL cible d'acces via le tunnel WireGuard
            target_url = f"http://{settings.VM2_WIREGUARD_IP}:{allocated_port}"

            return {
                "container_id": container.id,
                "container_name": container_name,
                "host": settings.VM2_WIREGUARD_IP,
                "port": allocated_port,
                "target_url": target_url,
                "runtime": chosen_runtime,
                "status": "running"
            }

        return await loop.run_in_executor(None, _sync_start)

    async def stop_challenge_instance(self, container_id: str) -> bool:
        """Detruit un conteneur sur la VM 2."""
        loop = asyncio.get_running_loop()

        def _sync_stop():
            try:
                container = self.client.containers.get(container_id)
                container.remove(force=True)
                return True
            except NotFound:
                return False
            except Exception as e:
                logger.error(f"Erreur destruction conteneur {container_id}: {e}")
                return False

        return await loop.run_in_executor(None, _sync_stop)

    async def get_instance_status(self, container_id: str) -> Optional[str]:
        """Recupere le statut d'un conteneur."""
        loop = asyncio.get_running_loop()

        def _sync_status():
            try:
                container = self.client.containers.get(container_id)
                return container.status
            except NotFound:
                return None

        return await loop.run_in_executor(None, _sync_status)


orchestrator_service = OrchestratorService()
