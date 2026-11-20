/**
 * Mocked CTF Challenges Data - V1 Specifications
 * 100% Web HTTPS via Traefik Reverse Proxy
 * Zero Lorem Ipsum - Realistic technical descriptions & scenarios
 * Docker images strictly conforming to the orchestrator whitelist (^ctf/...)
 */

export const mockChallenges = [
  {
    id: 'sqli-blind',
    title: 'SQL Injection — Blind (Boolean & Time-Based)',
    category: 'Web - Injection',
    categoryCode: 'WEB',
    author: 'SecurityLab',
    points: 35,
    difficulty: 3,
    solvedPercent: 64,
    borderAccent: 'border-emerald-500/80',
    badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    description: `Une interface d'authentification vulnérable filtre mal les entrées utilisateur sur le paramètre "username". Les messages d'erreur détaillés de la base PostgreSQL ont été désactivés en production.

En exploitant une technique d'injection SQL aveugle (inférence booléenne ou injections temporelles avec pg_sleep()), extrayez caractère par caractère le mot de passe du compte administrateur dissimulé dans la table "secret_vault".

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'sqli-blind-chal',
    targetUrl: 'https://a9f3b8c1.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-sqli-blind:1.0',
    flag: 'CTF{bl1nd_sql1_b00l34n_3xf1ltr4t10n}'
  },
  {
    id: 'xss-stored',
    title: 'XSS Stockée — Cookie Stealing & Session Hijacking',
    category: 'Web - Client-Side',
    categoryCode: 'WEB',
    author: 'AuditTeam',
    points: 25,
    difficulty: 2,
    solvedPercent: 71,
    borderAccent: 'border-blue-500/80',
    badgeColor: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    description: `Le module de commentaires de l'intranet étudiant permet de publier des avis publics. Un bot simulant le modérateur système consulte chaque nouveau message toutes les 30 secondes avec un navigateur headless.

L'absence d'assainissement HTML et l'absence de flag HttpOnly sur le cookie de session permettent d'injecter une charge JavaScript malveillante. Construisez un payload capable d'exfiltrer le cookie de session "ADMIN_TOKEN" vers votre collecteur HTTP pour usurper l'identité de l'administrateur.

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'xss-stored-chal',
    targetUrl: 'https://d4e7a2b9.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-xss-stored:1.0',
    flag: 'CTF{st0r3d_xss_c00k13_h1j4ck_succ3ss}'
  },
  {
    id: 'idor-profile',
    title: 'IDOR — Broken Object Level Authorization',
    category: 'Web - API & Auth',
    categoryCode: 'WEB',
    author: 'Admin',
    points: 20,
    difficulty: 1,
    solvedPercent: 82,
    borderAccent: 'border-emerald-500/80',
    badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    description: `L'API REST du portail de scolarité expose l'endpoint :
GET /api/v1/students/{uuid}/dossier

Le contrôle d'accès vérifie que vous êtes connecté, mais n'associe pas le jeton de session à la ressource demandée dans l'URI. En observant les requêtes réseau et en identifiant la structure des UUID, inspectez le dossier de l'examinateur principal "root_examiner" pour récupérer le flag de validation.

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'idor-api-chal',
    targetUrl: 'https://c1f8e4a7.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-idor-api:1.2',
    flag: 'CTF{1d0r_unpr0t3ct3d_4p1_3ndp01nt}'
  },
  {
    id: 'csrf-email',
    title: 'CSRF — Account Takeover sans SameSite',
    category: 'Web - Client-Side',
    categoryCode: 'WEB',
    author: 'SeisSiete',
    points: 30,
    difficulty: 2,
    solvedPercent: 58,
    borderAccent: 'border-blue-500/80',
    badgeColor: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    description: `Le formulaire de changement d'adresse de messagerie principale effectue une requête POST non protégée contre les attaques par falsification de requête inter-sites (aucun jeton CSRF et cookies de session sans attribut SameSite).

Concevez une page web externe qui force le navigateur de la victime connectée à envoyer une requête de mise à jour d'email vers votre adresse. Un script de simulation admin visitera votre exploit.

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'csrf-takeover-chal',
    targetUrl: 'https://e8b2c4d9.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-csrf-takeover:1.0',
    flag: 'CTF{csrf_4cc0unt_t4k30v3r_n0_s4m3s1t3}'
  },
  {
    id: 'ssrf-internal',
    title: 'SSRF — Intranet Reconnaissance & Cloud Metadata',
    category: 'Web - Server-Side',
    categoryCode: 'WEB',
    author: '0xCyber',
    points: 45,
    difficulty: 4,
    solvedPercent: 37,
    borderAccent: 'border-red-500/80',
    badgeColor: 'text-red-400 bg-red-500/10 border-red-500/30',
    description: `Une fonctionnalité d'export PDF télécharge les ressources web soumises par les utilisateurs pour convertir des rapports HTML. Le serveur applicatif n'applique aucun filtrage sur les adresses IP privées (RFC 1918) ni sur les schémas d'URL (file://, http://).

Exploitez cette faille SSRF pour interroger le service de métadonnées interne du cluster (169.254.169.254) et l'API d'administration interne accessible sur le port interne 8001 non exposé publiquement.

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'ssrf-pdf-chal',
    targetUrl: 'https://b7e3f1a2.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-ssrf-pdf:2.0',
    flag: 'CTF{ssrf_cl0ud_m3t4d4t4_3xf1ltr4t10n}'
  },
  {
    id: 'jwt-bypass',
    title: 'JWT Authentication Bypass — None Algorithm',
    category: 'Web - API & Auth',
    categoryCode: 'WEB',
    author: 'SecurityLab',
    points: 35,
    difficulty: 3,
    solvedPercent: 52,
    borderAccent: 'border-purple-500/80',
    badgeColor: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
    description: `L'application de gestion de serveurs confie les habilitations d'accès à un jeton JWT placé dans le header Authorization.

La bibliothèque de vérification cryptographique est mal configurée et accepte les en-têtes avec {"alg": "none"}. Retirez la signature du jeton, modifiez le payload avec {"role": "administrator", "is_admin": true} et présentez ce jeton falsifié à l'endpoint /admin/terminal pour débloquer le flag.

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'jwt-auth-chal',
    targetUrl: 'https://f2d9c1b8.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-jwt-bypass:1.1',
    flag: 'CTF{jwt_n0n3_4lg_byp4ss_c0nfus10n}'
  },
  {
    id: 'crypto-padding-oracle',
    title: 'Crypto Web — CBC Padding Oracle Attack',
    category: 'Web - Cryptographie',
    categoryCode: 'WEB',
    author: '0xDEADBEEF',
    points: 50,
    difficulty: 5,
    solvedPercent: 24,
    borderAccent: 'border-red-500/80',
    badgeColor: 'text-red-400 bg-red-500/10 border-red-500/30',
    description: `Le cookie de session "auth_data" chiffre en AES-128 CBC un objet JSON sérialisé. En cas d'erreur de déchiffrement due à un padding PKCS#7 incorrect, l'application renvoie un code HTTP 500 explicite ("Padding Exception"), tandis qu'un padding valide renvoie 200 ou 401.

Cette fuite d'information constitue un oracle de déchiffrement complet. Automatisez l'attaque par oracle de padding pour déchiffrer le cookie original, puis forgez un bloc chiffré octet par octet conférant les droits "superadmin: true".

Format du flag attendu : CTF{...}`,
    targetSubdomain: 'padding-oracle-chal',
    targetUrl: 'https://7a3b9c2e.chal.ctf.upjv.local',
    dockerImage: 'ctf/web-padding-oracle:1.0',
    flag: 'CTF{p4dd1ng_0r4cl3_c00k13_d3crypt_succ3ss}'
  }
]

export default mockChallenges
