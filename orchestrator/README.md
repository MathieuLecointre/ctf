# 🛡️ CTF Orchestrator Agent (VM 2)

Micro-service FastAPI exécuté en natif sur la **VM 2 (CHALLENGES - `10.1.136.73` / `10.10.10.2`)** pour piloter le cycle de vie des conteneurs vulnérables à la demande de l'API principale (VM 1).

---

## 🚀 Fonctionnalités & Sécurité

1. **Isolation stricte gVisor (`runsc`)** :
   * Chaque conteneur de challenge est exécuté avec le runtime durci gVisor (avec fallback sur `runc` si gVisor n'est pas encore installé).
   * Drop de toutes les capacités Linux (`cap_drop=['ALL']`).
   * Protection contre l'élévation de privilèges (`no-new-privileges: true`).
2. **Réseau par joueur** :
   * Chaque joueur dispose d'un bridge Docker isolé : `net_joueur{id_utilisateur}` sur le subnet `172.30.{id_utilisateur}.0/24`.
3. **Attribution dynamique de ports** :
   * Les conteneurs exposent leur service HTTP sur un port dynamique dans la plage `31001-31999` bindé sur l'adresse WireGuard `10.10.10.2`.
4. **Authentification mutuelle mTLS** :
   * Écoute sur le port **8443** chiffré et authentifié avec les certificats générés par l'équipe réseau (`ca.crt`, `server.crt`, `server.key`).

---

## 📦 Installation sur la VM 2

```bash
# 1. Cloner ou copier le dossier orchestrator/ sur la VM 2
cd /opt/ctf-orchestrator

# 2. Créer l'environnement virtuel Python
python3 -m venv .venv
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## 🔐 Configuration des Certificats mTLS

Placer les certificats dans `/opt/ctf-orchestrator/certs/` :
* `ca.crt` : Certificat de l'autorité racine commune.
* `server.crt` : Certificat serveur de la VM 2.
* `server.key` : Clé privée serveur de la VM 2.

---

## ▶️ Lancement manuel (Test)

```bash
uvicorn orchestrator.main:app \
  --host 10.10.10.2 \
  --port 8443 \
  --ssl-keyfile certs/server.key \
  --ssl-certfile certs/server.crt \
  --ssl-ca-certs certs/ca.crt \
  --ssl-cert-reqs 2
```
> Le flag `--ssl-cert-reqs 2` active l'exigence stricte du certificat client mTLS (rejet immédiat de tout client sans certificat valide émis par la CA).

---

## ⚙️ Déploiement en Service Systemd (Recommandé)

Créer le fichier `/etc/systemd/system/ctf-orchestrator.service` :

```ini
[Unit]
Description=CTF Orchestrator Agent (VM 2)
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ctf-orchestrator
ExecStart=/opt/ctf-orchestrator/.venv/bin/uvicorn orchestrator.main:app \
  --host 10.10.10.2 \
  --port 8443 \
  --ssl-keyfile certs/server.key \
  --ssl-certfile certs/server.crt \
  --ssl-ca-certs certs/ca.crt \
  --ssl-cert-reqs 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activer et démarrer le service :
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ctf-orchestrator
sudo systemctl status ctf-orchestrator
```
