import socket
import time
import os

# --- CONFIGURATION ---
DEST_IP = "10.129.188.115"    # Connexion directe par IP
DEST_PORT = 80                 # À changer si ton serveur TCP écoute sur un autre port (ex: 8080)
BUFFER_FILE = "data_buffer.json"
COMMAND_FILE = "command_flag.txt"

def extract_value(text, prefix):
    """Extrait une valeur numerique nettoyee apres un prefixe (T:, C: ou V:)"""
    if prefix in text:
        try:
            part = text.split(prefix)[1].lstrip()
            clean_part = part.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            value = clean_part.split(' ')[0].strip()
            return value
        except:
            return None
    return None

def send_data_via_tcp():
    """Lit le tampon, valide les donnees et envoie uniquement le JSON brut en TCP"""
    if not os.path.exists(BUFFER_FILE) or os.path.getsize(BUFFER_FILE) == 0:
        return

    # Lecture du fichier tampon
    f = open(BUFFER_FILE, "r")
    content = f.read()
    f.close()

    # Extraction des 3 constantes
    val_t = extract_value(content, "T:")
    val_c = extract_value(content, "C:")
    val_v = extract_value(content, "V:")

    # On n'envoie que si le triplet est complet pour la BDD
    if val_t and val_c and val_v:
        # Construction du texte JSON brut (uniquement la donnee)
        json_data = '{"temperature":"' + val_t + '", "tension":"' + val_v + '", "courant":"' + val_c + '"}'
        
        print("[TCP] Envoi de la donnee brute : " + json_data)
        
        try:
            # 1. Creation du Socket TCP (IPv4, TCP)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            # 2. Connexion TCP au serveur
            sock.connect((DEST_IP, DEST_PORT))
            
            # 3. Envoi UNIQUE de la donnée (Pas de HTTP, pas de headers)
            # On ajoute souvent un '\n' à la fin pour que le serveur sache que le message est fini
            packet = json_data + "\n"
            sock.sendall(packet.encode('utf-8'))
            
            # 4. Attente d'un accusé de réception brut (ex: "OK" ou "HEAT_ON")
            response = sock.recv(1024).decode('utf-8').strip()
            print("[TCP] Reponse brute du serveur : " + response)
            
            # Si le serveur renvoie quelque chose, on considère que c'est un succès
            if response:
                if "ON" in response:
                    print("[TCP] Ordre de chauffage detecte !")
                    f_cmd = open(COMMAND_FILE, "w")
                    f_cmd.write("ON")
                    f_cmd.close()
                
                # Succès : on vide le tampon local
                f_clear = open(BUFFER_FILE, "w")
                f_clear.close()
            
            # 5. Fermeture du socket
            sock.close()
            
        except Exception as e:
            print("[ERREUR TCP] Impossible de joindre le serveur : " + str(e))
    else:
        print("[TCP] Donnees incompletes dans le tampon.")

# --- BOUCLE PRINCIPALE ---
print("[*] Client TCP de donnees brutes demarre vers " + DEST_IP)
while True:
    send_data_via_tcp()
    time.sleep(10)
