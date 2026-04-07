import socket
import threading
import json
import time
import os
# Configuration
LOCAL_IP = '192.168.10.1' # IP de l'interface isolée du RPi
LOCAL_PORT = 1234
BUFFER_FILE = "data_buffer.json"
COMMAND_FILE = "command_flag.txt"

def handle_sensor_data(client_socket):
        try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                        print("[LOCAL] Données reçues : {}".format(data))
                        # Sauvegarde dans le fichier tampon (Append mode)
                        f = open(BUFFER_FILE, "a")
                        f.write(data + "\n")
                        f.close()

                        #Vérification si une commande attend d'être envoyée
                        if os.path.exists(COMMAND_FILE):
                                f_cmd = open(COMMAND_FILE, "r")
                                cmd = f_cmd.read().strip()
                                f_cmd.close

                                client_socket.send(cmd.encode('utf-8'))
                                print("[LOCAL] Commande envoyee")

                                try:
                                        os.remove(COMMAND_FILE)
                                except:
                                        pass
                        else:
                                client_socket.send("ACK".encode('utf-8'))
        except Exeption:
                print("[ERREUR LOCAL] : {]".format(sys.exc_info()[1]))
        finally:
                client_socket.close()

def start_local_serveur():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((LOCAL_IP, LOCAL_PORT))
        server.listen()
        print("[*] Serveur Local a l'ecoute sur {}:{}".format(LOCAL_IP, LOCAL_PORT))

        while True:
                client, addr = server.accept()
                # Un thread par connexion pour ne pas bloquer le  serveur
                client_handler = threading.Thread(target=handle_sensor_data, args=(client,))
                client_handler.start()

if __name__ == "__main__":
        start_local_serveur()

