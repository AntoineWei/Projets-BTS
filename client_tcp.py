import socket
#configuration
TCP_IP = '' #IP Rasberry
TCP_PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Creéer le socket client
client.connect((TCP_IP, TCP_PORT))  #Connection au Serveur

print("Envoi de la commande READ...")
client.send("READ".encode('utf-8')) #evoye de la commande
data = client.recv(1024).decode('utf-8')    #Recuperation de la reponse
print("Capteur:", data)


client.close()  #fermeture de la connexion 
