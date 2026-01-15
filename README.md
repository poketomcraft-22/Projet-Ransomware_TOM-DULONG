# 🛡️ Projet de Simulation Ransomware

## ⚠️ Avertissement Légal
Ce projet est réalisé dans un cadre strictement pédagogique pour le module de cybersécurité. L'objectif est de comprendre les mécanismes d'un serveur de contrôle (C2) et les vecteurs d'attaque par ransomware. Toute utilisation à des fins malveillantes est strictement interdite.

## 📝 Présentation du projet
Ce programme implémente une architecture Client/Serveur en Python. Il simule une attaque de ransomware complète, de l'exfiltration des clés au chiffrement des données, avec des capacités de gestion de fichiers à distance.

### Objectifs techniques remplis :
- **Identification unique** : Utilisation de l'UUID matériel de la victime.
- **Exfiltration de clé** : Envoi automatique de la clé XOR générée aléatoirement au serveur.
- **Manipulation système** : Exécution de commandes shell à distance (Remote Shell).
- **Transfert de fichiers robuste** : Upload et Download avec gestion de la taille des paquets pour éviter la corruption de données.
- **Chiffrement réversible** : Algorithme XOR appliqué récursivement sur un dossier cible.

---

## 📂 Arborescence du Projet
Le projet est organisé de manière à séparer l'environnement de l'attaquant de celui de la victime :

```text
Projet/
├── Client/
│   ├── client.py        # Le malware (exécuté sur la victime)
│   └── Fichier-DL.txt   # Fichier de test à exfiltrer (Download)
└── Serveur/
    ├── serveur.py       # Interface de contrôle (C2)
    ├── Fichier-Up.txt   # Fichier à envoyer sur la victime (Upload)
    └── base_victimes.txt # Journal des connexions et des clés reçues
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
1. Préparation du dossier cible
```text
Le malware cible spécifiquement le dossier ~/Documents/CIBLE. Si ce dossier est vide, le programme crée automatiquement un fichier témoin :
Fichier créé : coucou.txt contenant un message de test. Cela permet de démontrer le chiffrement même sur une machine vierge.
```
2. Lancement de la démonstration

Ouvrez deux terminaux Linux :
```bash
Terminal Attaquant (Serveur) :

cd ~/Python/Projet/Serveur
python3 serveur.py
```
Terminal Victime (Client) :
```bash
cd ~/Python/Projet/Client
python3 client.py
```
Connexion : 
```text
Le serveur affiche l'UUID et la clé de la victime. Ces infos sont sauvegardées dans `base_victimes.txt` qui est créer quand la première connexion est lancé.
```
## ⚙️ Détails de l'implémentation
Gestion des flux réseau:
```text
Pour les transferts de fichiers, le programme utilise un en-tête de 16 octets `ljust(16)`. Cet en-tête informe le destinataire de la taille exacte des données à recevoir, ce qui empêche le blocage des sockets TCP et permet de transférer des fichiers de n'importe quelle taille.
```
Sécurité du code:
```text
Si le serveur envoie une commande inconnue ou erronée, le client répond "Commande inconnue" au lieu de crasher. Cela maintient la synchronisation constante du flux.
```
