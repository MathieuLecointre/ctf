import asyncio
import json
import logging
from typing import Dict, List, Optional
from fastapi import WebSocket
import redis.asyncio as aioredis

from backend.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gestionnaire des connexions WebSocket pour le Scoreboard en temps reel.
    Diffuse instantanement les mises a jour de score a tous les clients connectes.
    Supporte Redis Pub/Sub pour une scalabilite multi-workers.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._redis_client: Optional[aioredis.Redis] = None
        self._pubsub_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket):
        """Accepte et enregistre une nouvelle connexion WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nouveau client connecte au scoreboard. Total : {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Retire une connexion fermee."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client deconnecte du scoreboard. Total restant : {len(self.active_connections)}")

    async def broadcast_json(self, data: Dict):
        """Diffuse un message JSON a tous les clients WebSockets actuellement connectes."""
        if not self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.warning(f"Erreur envoi WebSocket, marquage pour deconnexion : {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    async def notify_score_update(self, scoreboard_data: List[Dict]):
        """Notifie l'ensemble des navigateurs d'une mise a jour du tableau des scores."""
        message = {
            "type": "SCOREBOARD_UPDATE",
            "data": scoreboard_data
        }
        await self.broadcast_json(message)


# Singleton
scoreboard_ws_manager = ConnectionManager()
