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
    if os.stat("/home/ubuntu/.ssh/B_publickey.pem").st_size > 0:
       print("RSA key pairs already exist")
       pass
    else:
       key = RSA.generate(1024)
       f = open("/home/ubuntu/.ssh/B_privatekey.pem", "wb")
       f.write(key.exportKey('PEM'))
       f.close()

       pubkey = key.publickey()
       f = open("/home/ubuntu/.ssh/B_publickey.pem", "wb")
       f.write(pubkey.exportKey('OpenSSH'))
       f.close()
except OSError:
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
    Function to Encrypt the message and to get the ciphertext
    '''
    f = open("/home/ubuntu/.ssh/A_publickey.pem", "rb")
    key = RSA.importKey(f.read())
    x = key.encrypt(bytes(msg, "utf-8"), 32)
    return x[0]                           # we took this because we get a tuple 

#Function for decryption
def decryptt(msg):
    '''
    Function to Decrypt the cyphertext to btain the orignal message
    '''
    f1 = open("/home/ubuntu/.ssh/B_privatekey.pem", "rb")
    key1 = RSA.importKey(f1.read())
    z = key1.decrypt(msg) # try direct string
    return z.decode() 

def doagain():
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

    recived = s.recv(2048)
    string = recived
    output = str(string)[1:]

    if decryptt(string) == "exit":
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

    





