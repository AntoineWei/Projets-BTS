import socket
import time
import os

# --- CONFIGURATION ---
DEST_HOST = "10.129.188.115"  # IP du serveur de destination
DEST_IP = "10.129.188.115"    # Connexion directe par IP
DEST_PORT = 80                 # Port HTTP standard
BUFFER_FILE = "data_buffer.json"
COMMAND_FILE = "command_flag.txt"

def extract_value(text, prefix):
    """Extrait une valeur numerique nettoyee apres un prefixe (T:, C: ou V:)"""
    if prefix in text:
        try:
            part = text.split(prefix)[1].lstrip()
            # Remplace les sauts de ligne par des espaces pour isoler la donnee
            clean_part = part.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            value = clean_part.split(' ')[0].strip()
            return value
        except:
            return None
    return None

def send_data_via_tcp():
    """Lit le tampon, valide les donnees et forge la requete HTTP via Socket TCP"""
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
        # Construction du corps du message au format JSON attendu par le PHP
        json_data = '{"temperature":"' + val_t + '", "tension":"' + val_v + '", "courant":"' + val_c + '"}'
        
        print("[TCP] Envoi de la trame vers " + DEST_IP)
        
        try:
            # 1. Creation du Socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10) # Timeout pour eviter de bloquer le script
            
            # 2. Connexion TCP au serveur
            sock.connect((DEST_IP, DEST_PORT))
            
            # 3. Forge manuelle de la requete HTTP POST
            request = "POST /api/ajouterMesure.php HTTP/1.1\r\n"
            request += "Host: " + DEST_HOST + "\r\n"
            request += "Content-Type: application/json\r\n"
            request += "Content-Length: " + str(len(json_data)) + "\r\n"
            request += "Connection: close\r\n"
            request += "\r\n" # La ligne vide obligatoire qui separe les en-tetes du corps
            request += json_data
            
            # 4. Envoi de la requete forgee
            sock.sendall(request.encode('utf-8'))
            
            # 5. Reception de la reponse du serveur PHP
            response = sock.recv(4096).decode('utf-8')
            print("[TCP] Reponse brute du serveur recue.")
            
            # 6. Analyse du code retour HTTP
            if "200 OK" in response:
                print("[TCP] Enregistrement reussi avec succes.")
                
                # Verification de l'ordre de retour
                if "HEAT_ON" in response:
                    print("[TCP] Ordre de chauffage detecte dans la reponse !")
                    f_cmd = open(COMMAND_FILE, "w")
                    f_cmd.write("HEAT_ON")
                    f_cmd.close()
                
                # Succes de la chaine complète : on peut vider le tampon
                f_clear = open(BUFFER_FILE, "w")
                f_clear.close()
            else:
                print("[TCP] Erreur Serveur (Pas un code 200 OK)")
                
            # 7. Fermeture propre du socket
            sock.close()
            
        except Exception as e:
            print("[ERREUR TCP] Connexion impossible au serveur : " + str(e))
    else:
        print("[TCP] Donnees incompletes dans le tampon. Attente de T, C et V.")

# --- BOUCLE PRINCIPALE ---
print("[*] Lancement du Client TCP vers " + DEST_HOST)
while True:
    send_data_via_tcp()
    time.sleep(10) # Verifie le fichier toutes les 10 secondes (ajustable)
