import socket
import time
import random
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

def read_capteur():
    #Simule la lecture du capteur
    temp = 20 + random.uniform(-2, 5)   #18-25°C
    #Simule le courant 
    courant = 1.2 + random.uniform(-0.7, 0.8)   #0.5-2.0A
    return "TEMP:%.1fC COURANT:%2fA"% (temp, courant)

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
            valeur = read_capteur
            response = valeur.encode('utf-8')
        else:
            response = "Commande inconnue".encode('utf-8')  # Sans accent !
    
        client.send(response)
        print("-> Envoi;", response.decode('utf-8'))

    except Exception as e:
        print("Erreur:", e)
    
    client.close()
