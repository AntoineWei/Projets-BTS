import socket
import requests
#configuration
TCP_IP = '' #IP Rasberry
TCP_PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Creéer le socket client
client.connect((TCP_IP, TCP_PORT))  #Connection au Serveur

print("Envoi de la commande READ...")
client.send("READ".encode('utf-8')) #evoye de la commande
data = client.recv(1024).decode('utf-8')    #Recuperation de la reponse
print("Capteur:", data)

# Separe les données 
valeurs = dict(item.split(':') for item in data.split(' '))
temp = valeurs.get('temp', '0')
courant = valeurs.get('courant', '0')

# Envoi vers PHP 
php_url = 'http://.../enregistrer.php'  # ou IP distante
payload = {'temperature': temp, 'courant': courant}
response = requests.post(php_url, data=payload, timeout=5)

if response.status_code == 200:
    print("Données envoyées en BD:", response.text)
else:
    print("Erreur envoi:", response.status_code)

client.close()  #fermeture de la connexion
