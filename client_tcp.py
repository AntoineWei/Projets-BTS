import socket
import time
import os

# --- CONFIGURATION ---
DEST_IP = "10.129.188.115"    # Connexion directe par IP
DEST_PORT = 22                 # À changer si le serveur TCP écoute sur un autre port (ex: 8080)
BUFFER_FILE = "data_buffer.json"
COMMAND_FILE = "command_flag.txt"

# URL du serveur distant où se trouve le fichier .txt à récupérer
URL_FICHIER_DISTANT = "http://ton-serveur-distant.com/chemin/vers/ton/fichier.txt"

# --- FONCTIONS ---

def download_remote_file():
	"""Effectue une requête HTTP GET pour récupérer un fichier distant et le sauvegarder localement"""
	try:
		print("[HTTP] Connexion au serveur distant pour le fichier...")
		reponse = requests.get(URL_FICHIER_DISTANT, timeout=10)

		# On vérifie si la requête a réussi (code statut 200)
		if reponse.status_code == 200:
			print("[HTTP] Fichier récupéré avec succès !")
			
			# Sauvegarde du contenu dans un fichier local
			nom_fichier_local = "fichier_copie.txt"
			with open(nom_fichier_local, "w", encoding="utf-8") as fichier:
				fichier.write(reponse.text)
			print(f"[HTTP] Fichier sauvegardé localement sous : {nom_fichier_local}")
			
		else:
			print(f"[ERREUR HTTP] Impossible de récupérer le fichier. Code statut : {reponse.status_code}")

	except requests.exceptions.Timeout:
		print("[ERREUR HTTP] Le serveur distant a mis trop de temps à répondre (Timeout).")
	except requests.exceptions.ConnectionError:
		print("[ERREUR HTTP] Impossible de se connecter au serveur distant. Vérifie le réseau ou l'URL.")
	except Exception:
		print("[ERREUR HTTP] Une erreur imprévue est survenue.")

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
                # Récupération du fichier distant en HTTP
	            download_remote_file()
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
