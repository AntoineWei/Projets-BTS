import time
import os
import requests

API_URL = "http://projet.euroclimat.chez.com/api/ajouterMesure.php"
BUFFER_FILE = "data_buffer.json"
COMMAND_FILE = "command_flag.txt"

class CloudGateway:
        def __init__(self):
                self.running = True

        def extract_value(self, text, prefix):
                if prefix in text:
                        try:
                                part = text.split(prefix)[1]
                                part = part.lstrip()
                                clean_part = part.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                                value = clean_part.split(' ')[0].strip()
                                return value
                        except:
                                return None
                return None

        def send_to_api(self):
                if not os.path.exists(BUFFER_FILE) or os.path.getsize(BUFFER_FILE) == 0:
                        return

                # Lecture du fichier
                f = open(BUFFER_FILE, "r")
                content = f.read()
                f.close()

                temp = self.extract_value(content, "T:")
                curr = self.extract_value(content, "C:")
                volt = self.extract_value(content, "V:")

                if temp and curr and volt:
                        data_payload = {"temperature": temp, "tension": volt, "courant": curr}
                        print("[CLOUD] Envoi JSON: " + str(data_payload))

                        try:
                                #Requete HTTP POST
                                r = requests.post(API_URL, json=data_payload, timeout=10)

                                if r.status_code == 200:
                                        print("[CLOUD] Succes! Reponse: " + r.text)

                                        if "HEAT_ON" in r.text:
                                                print("[CLOUD] Commande HEAT_ON recue")
                                                f_cmd = open(COMMAND_FILE, "w")
                                                f_cmd.write("HEAT_ON")
                                                f_cmd.close()

                                        # On vide le tampon
                                        f_clear = open(BUFFER_FILE, "w")
                                        f_clear.close()
                                else:
                                        print("[CLOUD] Erreur HTTP: " + str(r.status_code))
                        except:
                                print("[CLOUD] Erreur: Impossible de joindre le serveur")
                else:
                        print("[CLOUD] Donnees incompletes dans le fichier")

        def main_loop(self):
                print("[*] Lancement de la passerelle...")
                while self.running:
                        self.send_to_api()
                        time.sleep(10)

if __name__ == "__main__":
        gateway = CloudGateway()
        gateway.main_loop()
