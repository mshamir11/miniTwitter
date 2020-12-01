import socket
import time
import os
import threading
import json
import pandas as pd
import datetime

#variables

HOST = "127.0.0.1"
PORT = 12345
BUFFER = 1024
START_ID = 10000

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST,PORT))
server_socket.listen(5)

#File Path
USER_DATABASE ='user_database.json'
TWEET_TABLE='tweet_table.json'      
USER_TO_ID =   'user_id.json'   

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
    
    
    user_database =open(USER_DATABASE, 'r+')
    user_to_id = open(USER_TO_ID,'r+')
    
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
        user_database =open(USER_DATABASE, 'r+')
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
                  user_to_id = open(USER_TO_ID,'w')
                  user_database =open(USER_DATABASE, 'w')
                  user_database.write(json.dumps(data,indent=4))
                  user_to_id.write(json.dumps(user_to_id_dict,indent=4))
                  user_to_id.close()
                  user_database.close()
                  break
                 
        print("Im here")

def feeds(client_sockt,user_id):
    print("feeds")
    
def postTweet(client_sockt,user_id):
    sendMessage("Please type your tweet to be posted",client_sockt)
    tweet = client_sockt.recv(10000).decode()
    tweet_table_df = pd.read_csv('tweet_table.csv')
    tweet_id = tweet_table_df.iloc[-1]['tweet_id']+1
    user_id = user_id
    date_time = datetime.datetime.now()
    tweet_dic = {'tweet_id': [tweet_id], 'content': [tweet], 'useer_id': [user_id],'date_time_created':[date_time],'last_update_time':[date_time]} 
    df_temp =pd.DataFrame(tweet_dic) 
    tweet_table_df= tweet_table_df.append(df_temp,ignore_index=True)
    tweet_table_df.to_csv('tweet_table.csv', header=True, index=False)
    
    sendMessage("Tweet posted. \n 1. Home page. \n 2. Post Another tweet \n 3. Quit ",client_sockt)
    response = client_sockt.recv(30).decode()
    
    if response=='1':
        homePage(client_sockt,user_id)
    elif response =='2':
       postTweet(client_sockt,user_id)
    
    elif response=='3':
        logOut(client_sockt) 
        
def searchByName(client_socket,user_id):
    print("search by name")


def followUser(client_socket,user_id):
    print("Follow this user")

def listOfFollowers(client_socket,user_id):
    print("List of followers")
    
    
def individualUser(client_socket,user_id,user_name):
    sendMessage(f"Welcome to {user_name}'s page. \n 1. Feeds \n 2. Follow this user. \n 3. List of followers",client_socket)
    response = client_socket.recv(10)
    
    if response=='1':
        feeds(client_socket,user_id)
    elif response =='2':
       followUser(client_socket,user_id)
    
    elif response=='3':
        listOfFollowers(client_socket) 
    
    

def listOfUsers(client_socket,user_id):
    print("List of users")
    user_to_id = open(USER_TO_ID,'r+')
    user_to_id_dict = json.load(user_to_id)
    message =""
    for i,key in enumerate(user_to_id_dict.keys()):
        if len(key)>0:
         message += f"{i+1}. {key} \n"
    sendMessage(message,client_socket)
    response = client_socket.recv(10).decode()
    for i,key in enumerate(user_to_id_dict.keys()):
        if response==str(i+1):
            individualUser(client_socket,user_to_id[key],key)
            break

def searchPeople(client_sockt,user_id):    
    print ("Search People")
    sendMessage("1. List of registered users. \n 2. Search for user by name",client_sockt)
    response = client_sockt.recv(30).decode()
    
    if response=='1':
        listOfUsers(client_sockt,user_id)
    elif response =='2':
       searchByName(client_sockt,user_id)
    
def chat(client_sockt,user_id):      
    print("Chat")
      
def logOut(client_sockt):
    print("Log out page")
    sendMessage("You have been successfull Logged out.\n 1. Login Page \n 2. Quit",client_sockt)
    response = client_sockt.recv(30).decode()
    
    if response=='1':
        loginPage(client_sockt)
    
    elif response=='2':
        client_sockt.close()
             
def homePage(client_sockt,user_id):
    print("Im at home page")        
    sendMessage("Home Page \n1. Feeds\n2. Post a tweet\n3. Search People\n4. Chat",client_sockt)
    response = client_sockt.recv(30).decode()
    
    if response=='1':
        feeds(client_sockt,user_id)
    
    elif response=='2':
        postTweet(client_sockt,user_id)
    
    elif response=='3':
        searchPeople(client_sockt,user_id)
    
    elif response=='4':
        chat(client_sockt,user_id)
    
    elif response=='8':
        logOut(client_sockt)            
    else:
        homePage(client_sockt,user_id)
    
def existingUser(client_socket):
    
    
    print("Welcome Old User")
    user_database =open(USER_DATABASE, 'r')
    user_to_id = open(USER_TO_ID,'r')
    data =json.load(user_database)
    user_to_id_dict = json.load(user_to_id)
    sendMessage("Please Enter your username:",client_socket)
    user_name = client_socket.recv(30).decode()
    sendMessage("Please Enter your password: ",client_socket)
    password = client_socket.recv(30).decode()
    
    while True:
        
     try: 
        if data[str(user_to_id_dict[user_name])]['password']==password :
            homePage(client_socket,str(user_to_id_dict[user_name]))
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
    
    
        
    
    
    