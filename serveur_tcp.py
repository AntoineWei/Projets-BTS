import socket
import threading
import json
import time
import os
import sys

# Configuration
LOCAL_IP = '192.168.10.1' # IP de l'interface isolée du RPi
LOCAL_PORT = 1234
BUFFER_FILE = "data_buffer.json"
COMMAND_FILE = "command_flag.txt"

def handle_sensor_data(client_socket):
    try:
        while True:
            # Réception des données du capteur
            data = client_socket.recv(1024).decode('utf-8')
            
            # Déconnexion propre du client
            if not data:
                print("[LOCAL] Le client a ferme la connexion.")
                break
                
            print("[LOCAL] Donnees recues : {}".format(data))
            
            # Sauvegarde dans le fichier tampon
            f = open(BUFFER_FILE, "a")
            f.write(data + "\n")
            f.close()

            # Vérification du fichier de commande
            if os.path.exists(COMMAND_FILE):
                try:
                    f_cmd = open(COMMAND_FILE, "r")
                    cmd_content = f_cmd.read().strip()
                    f_cmd.close()

                    # On s'assure qu'on a bien le format "OFF:X"
                    if "OFF:" in cmd_content:
                        # On sépare "OFF" et la valeur de la tempo (X)
                        parts = cmd_content.split(":")
                        delai = float(parts[1])
                        
                        # 1. Envoi immédiat de la commande ON
                        client_socket.send("ON".encode('utf-8'))
                        print("[LOCAL] Commande ON envoyee. Debut de la temporisation de {}s...".format(delai))
                        
                        # 2. Attente de X secondes
                        time.sleep(delai)
                        
                        # 3. Envoi de la commande OFF
                        client_socket.send("OFF".encode('utf-8'))
                        print("[LOCAL] Temporisation ecoulee : Commande OFF envoyee.")
                        
                        # Suppression du fichier de commande après exécution complète
                        try:
                            os.remove(COMMAND_FILE)
                        except:
                            pass
                    else:
                        # Si le fichier contient autre chose ou n'est pas bien formaté
                        client_socket.send("ACK".encode('utf-8'))
                        
                except Exception:
                    print("[ERREUR CONFIG] Impossible de traiter le fichier de commande : {}".format(sys.exc_info()[1]))
                    client_socket.send("ACK".encode('utf-8'))
            else:
                # Comportement standard : pas de commande en attente, on valide juste la réception
                client_socket.send("ACK".encode('utf-8'))
                print("[LOCAL] ACK envoye")

    except Exception:
        print("[ERREUR LOCAL] : {}".format(sys.exc_info()[1]))
    finally:
        print("[LOCAL] Fermeture de la connexion client.")
        client_socket.close()

def start_local_serveur():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCAL_IP, LOCAL_PORT))
    server.listen()
    print("[*] Serveur Local a l'ecoute sur {}:{}".format(LOCAL_IP, LOCAL_PORT))

    while True:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_sensor_data, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    start_local_serveur()
