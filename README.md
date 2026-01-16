# A FAIRE SUR UN DEBIAN OU AUTRE LINUX SUR LE MÊME NOYAU
# 🛡️ Projet de Simulation Ransomware
## 📝 Présentation du projet
Ce programme implémente une architecture **Client/Serveur** en Python simulant un Ransomware piloté par un serveur. Il permet de comprendre les mécanismes d'exfiltration, de chiffrement et de contrôle à distance.

### Fonctionnalités implémentées :
- **Identification unique** : Récupération de l'UUID matériel via `/proc/sys/kernel/random/uuid`.
- **Exfiltration automatique** : Envoi immédiat de l'identifiant et de la clé de chiffrement au serveur dès la connexion.
- **Remote Shell** : Exécution de commandes système Linux (ls, whoami, etc.) avec retour de la sortie console.
- **Transfert de fichiers bidirectionnel** : Fonctions `upload` (serveur vers client) et `download` (client vers serveur).
- **Cryptographie XOR** : Chiffrement et déchiffrement récursif d'un dossier cible (`~/Documents/CIBLE`).
- **Système de Logs complet** : Tracabilité des actions côté serveur et côté client.

---

## 🏗️ Architecture Globale
Le projet repose sur un modèle **Client/Serveur** utilisant des sockets TCP :

1.  **Le Serveur (Attaquant)** : Reste en écoute (`0.0.0.0`) sur le port `9526`. Il centralise les clés exfiltrées et envoie les ordres.
2.  **Le Client (Malware)** : Se connecte au serveur, envoie ses identifiants et attend les instructions en boucle.
3.  **Communication** : Utilisation de protocoles de messages avec préfixes de taille (16 octets) pour assurer l'intégrité des transferts de fichiers.

---

## 📂 Arborescence du Projet
Le projet est organisé de manière à séparer l'environnement de l'attaquant de celui de la victime :

```text
Projet/
├── Client/
│   ├── client.py          # Le malware
│   ├── Fichier-DL.txt     # Fichier à exfiltrer (test download)
│   └── .client_debug.log  # Log local caché (généré à l'exécution)
└── Serveur/
    ├── serveur.py         # Interface de contrôle
    ├── Fichier-Up.txt     # Fichier à propager (test upload)
    ├── base_victimes.txt  # Stockage persistant des clés exfiltrées (généré à l'exécution)
    └── logs.txt           # Historique complet des actions (généré à l'exécution)
```
## 🛠️ Guide des Commandes
| Commande | Action |
| :--- | :--- |
| `chiffrer` | Chiffre les fichiers du dossier `~/Documents/CIBLE`. |
| `dechiffrer` | Déchiffre les fichiers pour restaurer l'accès. |
| `system` | Lance une commande système (ex: `ls`, `whoami`, `pwd`). |
| `upload` | Envoie un fichier présent sur le serveur vers la victime (ex: `Fichier-UP.txt`). |
| `download` | Récupère un fichier présent chez la victime vers le serveur(ex: `Fichier-DL.txt`). |
| `quitter` | Ferme la session de contrôle proprement. |

## 🚀 Protocole de Test
### 1. Préparation du dossier cible
Le malware cible le dossier `~/Documents/CIBLE.` S'il est absent ou vide, le client crée automatiquement `coucou.txt` pour permettre le test de chiffrement.

### 2. Lancement de la démonstration
Ouvrez deux terminaux Linux :

**Terminal Attaquant** (Serveur) :
```bash
cd ~/Python/Projet/Serveur
python3 serveur.py
```
**Terminal Victime** (Client) :
```bash
cd ~/Python/Projet/Client
python3 client.py
```

## 📜 Système de Logs (Traçabilité)

Le projet intègre une gestion avancée des événements pour l'analyse a posteriori :

    - **Logs Serveur** (`logs.txt`) : Horodatage et classification des événements (`INFO`, `ACTION`, `ERROR`, `EXFILTRATION`) pour surveiller le parc de machines.

    - **Logs Client** (`.client_debug.log`) : Fichier caché sur la machine victime (préfixe `.`) permettant à l'attaquant de vérifier le bon fonctionnement du malware sans alerter l'utilisateur.

## ⚙️ Fonctionnement du Protocole

Le protocole de communication est conçu pour être robuste :

    - **Synchronisation** : Pour chaque transfert (Upload/Download), un en-tête de 16 octets informe le destinataire de la taille des données à lire.

    - **Résilience** : Un bloc de sécurité `else` dans la boucle client intercepte les commandes inconnues pour éviter que le malware ne s'arrête en cas d'erreur de saisie sur le serveur.

## ⚠️ Limites et Faiblesses

Bien que fonctionnel, ce ransomware présente des limites par rapport à une menace réelle :

    - **Chiffrement Symétrique (XOR)** : La clé est la même pour chiffrer et déchiffrer. Si la clé est interceptée, le déchiffrement est trivial.

    - **Absence d'Obfuscation** : Le code est en clair (Python) et facilement détectable par une analyse statique ou un antivirus.

    - **Communication Non-Chiffrée** : Les échanges entre le client et le serveur circulent en clair sur le réseau (pas de TLS/SSL), ce qui permet à un IDS (Système de Détection d'Intrusion) de lire les commandes.

    - **Persistance** : Le malware ne se relance pas automatiquement au redémarrage de la machine.
