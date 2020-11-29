import socket
import time
import os
import argparse
import threading
import json

#Argument Parser Section
ap =argparse.ArgumentParser()
ap.add_argument("-i","--index",help ="index to the dictionary")
ap.add_argument("-p","--persistent",help ="1 for persistent 0 for non persistent")
args = vars(ap.parse_args())


#variables

HOST = "127.0.0.1"
PORT = 12345
BUFFER = 1024
START_ID = 10000
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST,PORT))
server_socket.listen(5)

RESULT_PATH ='user_database.json'
            
        

def sendMessage(message,client_socket):
    try:
        client_socket.send(bytes(message,'utf-8'))
    
    except:
        print("Sending Error")

def loginPage(client_socket):
    sendMessage("Welcome To Mini-Twitter \n Choose the following: \n 1. New User \n 2. Existing User\n",client_socket)
    user_response = client_socket.recv(10).decode()
    print(user_response)
    
    if user_response=='1':
        newUser(client_socket)
    elif user_response=='2':
        existingUser(client_socket)

def newUser(client_socket):
    
    
    user_database =open(RESULT_PATH, 'r+')
    user_to_id = open('user_id.json','r+')
    
    user_database_dict = user_database.read()
    if len(user_database_dict)==0:
        
        
        sendMessage("Welcome New User \n please enter a user name: \n",client_socket)
        user_name = client_socket.recv(30).decode()
        sendMessage("Please Enter a password: ",client_socket)
        password = client_socket.recv(30).decode()
        dictionary = {0:{'id_start':START_ID+1},START_ID+1:{'user_name':user_name,"password":password,"following":[]}}
        user_database.write(json.dumps(dictionary,indent=4))
        user_id_dict ={user_name:START_ID+1}
        user_to_id.write(json.dumps(user_id_dict,indent=4))
    
    else:
        user_database =open(RESULT_PATH, 'r+')
        data =json.load(user_database)
        user_to_id_dict = json.load(user_to_id)
        sendMessage("Welcome New User \nPlease enter a user name: \n",client_socket)
        user_name = client_socket.recv(30).decode()
        while True:
            
            
            try:
                user_to_id_dict[user_name]
                sendMessage("The user name already exist.Please enter a different user_name : ",client_socket)
                user_name = client_socket.recv(30).decode()
                
            except:
                  sendMessage("Please Enter a password: ",client_socket)
                  password = client_socket.recv(30).decode()
                  data[data['0']['id_start']+1]={'user_name':user_name,"password":password,"following":[]}
                  user_to_id_dict[user_name]=data['0']['id_start']+1
                  data['0']['id_start']=data['0']['id_start']+1
                  user_database.close()
                  user_to_id.close()
                  user_to_id = open('user_id.json','w')
                  user_database =open(RESULT_PATH, 'w')
                  user_database.write(json.dumps(data,indent=4))
                  user_to_id.write(json.dumps(user_to_id_dict,indent=4))
                  user_to_id.close()
                  user_database.close()
                  break
                 
        print("Im here")
            
            
def homePage(client_sockt):
    print("Im at home page")        
    sendMessage("")            
        
    
def existingUser(client_socket):
    
    
    print("Welcome Old User")
    user_database =open(RESULT_PATH, 'r')
    user_to_id = open('user_id.json','r')
    data =json.load(user_database)
    user_to_id_dict = json.load(user_to_id)
    sendMessage("Please Enter your username:",client_socket)
    user_name = client_socket.recv(30).decode()
    sendMessage("Please Enter your password: ",client_socket)
    password = client_socket.recv(30).decode()
    while True:
        
        
        try:
            if data[str(user_to_id_dict[user_name])]['password']==password :
                homePage(client_socket)
                break
            else:
                sendMessage("Incorrect Password. Please re-enter correct the password",client_socket)
                password = client_socket.recv(30).decode()
                
            
        except:
            sendMessage("Username does not exist. Please Enter the correct username: ",client_socket)
            user_name = client_socket.recv(30).decode()
                
    
    
def persistentThread(client_socket,address):
   
    print(f"User with {address} connected")
    loginPage(client_socket)
    
        
    
    
def persistentConnection():
    
    client_socket, address = server_socket.accept()
    threading._start_new_thread(persistentThread,(client_socket,address))



print("Twitter Server Started....")
while True:
    persistentConnection()
    
    
        
    
    
    