import socket
import time
import random
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

def read_capteur():
    #Simule la lecture du capteur
    temp = 20 + random.uniform(-2, 5)   #18-25°C
    return "TEMP:%.1fC" % temp

#Serveur TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(5)
print("Serveur TCP sur port 12345...")

while True:
    client, addr = server.accept()
    print("Connexion {}".format(addr))

    try:
        data = client.recv(1024).decode('utf-8')
    
        if data == "READ":
            valeur = read
            response = "temp:25.3C humid:60%".encode('utf-8')
        else:
            response = "Commande inconnue".encode('utf-8')  # Sans accent !
    
        client.send(response)
        print("-> Envoi;", response.decode('utf-8'))

    except Exception as e:
        print("Erreur:", e)
    
    client.close()
