import socket
import requests
import json

# Configuration de la connexion
TCP_IP = '192.168.10.1' # Ecoute sur toutes les interfaces du Raspberry
TCP_PORT = 8080         # Port à ouvrir
WEB_SERVEUR_URL = ""    #URL Serveur WEB

#Dictionnaire pour stocker les données
donnee = {
        "temperature": None,
        "courant": None,
        "tension": None
}

def envoi_au_serveurw(payload):
        """Envoie les données recues au serveur"""
        try:
                print("Envoi groupé au serveur WEB : {}".format(payload))
                response = requests.post(WEB_SERVEUR_URL, json=payload, timeout=5)
                if reponse.status_code == 200:
                        print("Succes : Donnees transmises.")
                else:
                        print("Erreur Serveur WEB : {}".format(response.status_code))
        except Exception:
                err = sys.exc_info()[1]
                print("Erreur HTTP : {}".format(err))

def start_serveur():
        # Création du socket TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #permet de relancer le script sans attendre que le port se libère
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
                server_socket.bind((TCP_IP, TCP_PORT))
                server_socket.listen(5)
                print("Serveur TCP actif sur le port {}".format(TCP_PORT))
        except Exeption:
                err = sys.exc_info()[1]
                print("Impossible de demarrer le serveur : {}".format(err))
                return

        while True:
                #Attend une connexion des capteurs
                conn,addr = server_socket.accept()

                try:
                        print("Connecte par {}".format(addr))
                        raw_data = conn.recv(1024)
                        if raw_data:
                                message = raw_data.decode('utf-8').strip()

                        #Logique de tri
                        mots = message.split()
                        for mot in mots:
                                if mot.startswith("T:"):
                                        donnee["temperature"] = mot.replace("T:", "")
                                elif mot.startswith("C:"):
                                        donnee["courant"] = mot.replace("C:", "")
                                elif mot.startswith("V:"):
                                        donnee["tension"] = mot.replace("V:", "")


                        # Verification des données
                        if donnee["temperature"] and donnee["courant"] and donnee["tension"]:
                                #Envoie des donnee
                                envoi_au_serveurw(donnee)

                                #Vide les donnee pour les prochaine
                                donnee["temperature"] = None
                                donnee["courant"] = None
                                donnee["tension"] = None
                                print("Donnee reinitialisé.")
                        else:
                                print("Données partielles recues. Etat actuel : {}".format(donnee))


                except Exception:
                        err = sys.exc_info()[1]
                        print("Erreur lors de la reception : {}".format(err))
                finally:
                        conn.close()

if __name__ == "__main__":
        start_serveur()
