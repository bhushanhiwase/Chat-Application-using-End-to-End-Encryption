import socket
import sys
import os
from Crypto.PublicKey import RSA

HOST = '192.168.64.129'  # The server's hostname or IP address
PORT = 65435      # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("connection to the host is successful..")

flag = False
# check and create RSA key pairs here.

try:
    if os.stat("/home/ubuntu/.ssh/B_publickey.pem").st_size > 0:        # checks if key is aready present i.e. pem file has key data
       print("RSA key pairs already exist")                             # If size greater than 0 bytes then file exist
       pass
    else:
       key = RSA.generate(1024)                                          # Generates key if it doesn't exist
       f = open("/home/ubuntu/.ssh/B_privatekey.pem", "wb")
       f.write(key.exportKey('PEM'))
       f.close()

       pubkey = key.publickey()
       f = open("/home/ubuntu/.ssh/B_publickey.pem", "wb")
       f.write(pubkey.exportKey('OpenSSH'))
       f.close()
except OSError:                                                            # If there is no pem file then generate keys
    print("No file found, creating a new one....")
    flag = True
    key = RSA.generate(1024)
    f = open("/home/ubuntu/.ssh/B_privatekey.pem", "wb")
    f.write(key.exportKey('PEM'))
    f.close()

    pubkey = key.publickey()
    f = open("/home/ubuntu/.ssh/B_publickey.pem", "wb")
    f.write(pubkey.exportKey('OpenSSH'))
    f.close()

# sendong and reciving public keys

data = s.recv(1024)
file = open("/home/ubuntu/.ssh/A_publickey.pem", "wb")
file.write(data)
file.close()

file = open("/home/ubuntu/.ssh/B_publickey.pem", "rb")
data = file.read()
s.send(data)
file.close()

#Function for encryption
def encrypt(msg):
    '''
    Function to Encrypt the message with public key and to get the ciphertext
    '''
    f = open("/home/ubuntu/.ssh/A_publickey.pem", "rb")
    key = RSA.importKey(f.read())                                   
    x = key.encrypt(bytes(msg, "utf-8"), 32)                        # Encryption done using public key          
    return x[0]                           # we took this because we get a tuple 

#Function for decryption
def decryptt(msg):
    '''
    Function to Decrypt the cyphertext to btain the orignal message
    '''
    f1 = open("/home/ubuntu/.ssh/B_privatekey.pem", "rb")
    key1 = RSA.importKey(f1.read())
    z = key1.decrypt(msg) # try direct string
    return z.decode()           # Decode the bytes data into string format, can use str(z, "utf-8")

def doagain():
    '''
   Function to handle the exception while user tries to send empty string
   '''
    data = input("msg to A: ")
    if data:
        s.send(bytes(data, 'utf-8'))
        if data == "exit":
            if flag == True:
                os.remove("/home/ubuntu/.ssh/A_publickey.pem")
            sys.exit()
    else:
        doagain()

#Function used to send messages
def sendmsg():
    '''
   Function for sending messages to the other user
   '''
    data = input("msg to A: ")
    if data:
        s.send(encrypt(data))
        if data == "exit":
            if flag == True:
                os.remove("/home/ubuntu/.ssh/A_publickey.pem")
            sys.exit()
    else:
        doagain()

#Function used to receive messages
def recvmsg():
    '''
   Function for reciving messages from the user
   '''
    recived = s.recv(2048)
    string = recived
    output = str(string)[1:]

    if decryptt(string) == "exit":
        '''
   Function for decrypting cypher text to get back orignal message
   '''
        print("A left the chatroom...")
        sys.exit()
    elif len(string) > 0:
        print("msg from A: ", "Orignal Message:",decryptt(string))
        print("Cipher text:", output)
    else:
        doagain()

while True:

    sendmsg()
    recvmsg()

    





