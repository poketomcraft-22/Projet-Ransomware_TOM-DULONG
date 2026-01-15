# 🛡️ Projet de Simulation Ransomware (C2)

## ⚠️ Avertissement Éthique
Ce projet est réalisé dans un cadre strictement pédagogique pour le module de cybersécurité. L'objectif est de comprendre le fonctionnement d'un serveur de Command & Control (C2) et les mécanismes de chiffrement. Toute utilisation malveillante est interdite.

## 📝 Présentation du projet
Ce programme implémente une architecture Client/Serveur en Python permettant de simuler une attaque par ransomware. Il répond aux exigences techniques de gestion de parc de machines et de manipulation de données à distance.

### Fonctionnalités obligatoires (implémentées) :
- **Identification** : Génération d'un UUID unique par machine victime.
- **Exfiltration** : Envoi immédiat de la clé de chiffrement XOR au serveur.
- **Remote Shell** : Exécution de commandes système sans privilèges administrateur avec retour de la sortie.
- **Chiffrement/Déchiffrement** : Algorithme XOR appliqué récursivement sur un dossier cible.
- **Transfert de fichiers** : Upload (serveur vers client) et Download (client vers serveur).

---

## 🛠️ Utilisation et Commandes

| Commande | Action |
| :--- | :--- |
| `chiffrer` | Chiffre les fichiers du dossier `~/Documents/CIBLE`. |
| `dechiffrer` | Déchiffre les fichiers pour restaurer l'accès. |
| `system` | Lance une commande système (ex: `ls`, `whoami`, `pwd`). |
| `upload` | Envoie un fichier présent sur le serveur vers la victime. |
| `download` | Récupère un fichier présent chez la victime vers le serveur. |
| `quitter` | Ferme la session de contrôle proprement. |

---

## 🚀 Protocole de Test

### 1. Préparation (Côté Client)
Créez un dossier cible et un fichier de test pour vérifier le chiffrement :
```bash
mkdir -p ~/Documents/CIBLE
echo "Données confidentielles" > ~/Documents/CIBLE/secret.txt
```
2. Exécution

Lancez le serveur d'abord, puis le client dans deux terminaux séparés :
```bash
# Terminal Serveur
python3 serveur.py

# Terminal Client
python3 client.py
```
3. Démonstration des transferts

    Pour l'Upload : Placez un fichier test.txt dans le dossier serveur, tapez upload et entrez le nom.

    Pour le Download : Tapez download et entrez Documents/CIBLE/secret.txt. Le fichier apparaîtra sur le serveur avec le préfixe DL_.

⚙️ Détails Techniques
Synchronisation et Robustesse

    Gestion des Octets : Utilisation du préfixe b"" et de .encode()/.decode() pour la communication socket.

    Préfixe de Taille : Les transferts de fichiers utilisent un en-tête de 16 octets (ljust(16)) pour annoncer la taille des données, évitant ainsi la saturation ou le blocage du flux TCP.

    Gestion d'Erreurs : Utilisation de clauses else et de vérifications os.path.exists pour empêcher le crash du client en cas de commande invalide ou de fichier manquant.
