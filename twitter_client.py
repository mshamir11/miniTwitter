

import socket
import time
import os
import json
import subprocess
import sys
import argparse
import getpass
import stdiomask

#variable
IP_ADDRESS = "127.0.0.1"
PORT = 12345
BUFFER = 1024


        
def persistentConnection(IP_ADDRESS,PORT):
    
    
   client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   client_socket.connect((IP_ADDRESS,PORT))
   
  
   while True:
    data = client_socket.recv(1024).decode()
    print(data)
    if data[-9:-1]=="password":
        input_resp = stdiomask.getpass("Enter a input:")
    else:
        input_resp = input("Enter your input: ")
    
    if input_resp=='exit':
        break
    client_socket.send(bytes(input_resp,'utf-8'))
   
    

if __name__ == '__main__':
    persistentConnection(IP_ADDRESS,PORT)
    