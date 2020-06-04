import socket
import sys
from Crypto.PublicKey import RSA
import os

HOST = '192.168.64.129'  # Standard loopback interface address (localhost)
PORT = 65435  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
client, addr = s.accept()
print("Connection to client (B) is successful....")

flag = False                   #Flag to check if files were exchanged before the conversation

# check and create  RSA Key pairs
try:
   if os.stat("/home/ubuntu/.ssh/A_publickey.pem").st_size > 0:
       print("RSA key pairs already exist")
       pass
   else:
       key = RSA.generate(1024)
       f = open("/home/ubuntu/.ssh/A_privatekey.pem", "wb")
       f.write(key.exportKey('PEM'))
       f.close()
  
       pubkey = key.publickey()
       f = open("/home/ubuntu/.ssh/A_publickey.pem", "wb")
       f.write(pubkey.exportKey('OpenSSH'))
       f.close()
except OSError:

   print("No file found, creating a new one....")
   flag = True

   key = RSA.generate(1024)
   f = open("/home/ubuntu/.ssh/A_privatekey.pem", "wb")
   f.write(key.exportKey('PEM'))
   f.close()

   pubkey = key.publickey()
   f = open("/home/ubuntu/.ssh/A_publickey.pem", "wb")
   f.write(pubkey.exportKey('OpenSSH'))
   f.close()

# Send and receive each others  public keys
file = open("/home/ubuntu/.ssh/A_publickey.pem", "rb")          #/.ssh is the location where files are to be saved
data = file.read()
client.send(data)
file.close()

rec = client.recv(1024)
file2 = open("/home/ubuntu/.ssh/B_publickey.pem", "wb")
file2.write(rec)
file2.close()


# function for encryption
def encrypt(msg):              
   '''
    Function to encrypt message before sending
   '''
   f = open("/home/ubuntu/.ssh/B_publickey.pem", "rb")
   key = RSA.importKey(f.read())
   x = key.encrypt(bytes(msg, "utf-8"), 32)
   return x[0]                        # returns the string


def decryptt(msg):                  
   '''
   Function to decrypt the cyphertext into orignal Message
   '''
   f1 = open("/home/ubuntu/.ssh/A_privatekey.pem", "rb")
   key1 = RSA.importKey(f1.read())
   z = key1.decrypt(msg)
   return z.decode("utf-8")


def doagain():  
   '''
   Function to handle the exception while user tries to send empty string
   '''
   z = input("msg to B: ")
   if z:
       client.send(encrypt(z))
       if z == "exit" and flag == True:             # to check if RSA pair files were created and later to remove them
           os.remove("/home/ubuntu/.ssh/B_publickey.pem")
           sys.exit()
       elif z == 'exit':
           sys.exit()
   else:
       doagain()


def sendmsg():     
   '''
   Function for sending messages to the other user
   '''
   z = input("msg to B: ")
   if z:
       client.send(encrypt(z))
       if z == "exit" and flag == True:
           os.remove("/home/ubuntu/.ssh/B_publickey.pem")
           sys.exit()
       elif  z == "exit":
           sys.exit()
   else:                            # it is like gotto statement
        doagain()

def recvmsg():                      
   '''
   Function to receive messages
   '''
   data = client.recv(2048)
   string = data
   if decryptt(string) == "exit" and flag == True:
       print("B left the chatroom...")
       os.remove("/home/ubuntu/.ssh/B_publickey.pem") 
       sys.exit()
   elif decryptt(string) == "exit":
       print("B left the chatroom...") 
       sys.exit()
   else:
       print("msg from B :","orignal Message:", decryptt(string))
       print("Cipher text:", str(data)[1:])

while True:
   
    recvmsg()
    sendmsg()    




