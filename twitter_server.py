import socket
import time
import os
import threading
import json
import pandas as pd
import datetime
import sys
import re
import crypt
from hmac import compare_digest as compare_hash

#variables


'''
Things to do


  3. Password encryption
  3. List of followers

'''



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
TWEET_TABLE = 'tweet_table.csv'
HASHTAG = 'hashtag.json'
HASHTAG_COUNT = 'hashtag.csv'
ACTIVE_USERS ='active_users.csv'

'''
The name in the brackets is the respective function name
Client Side View: 

    login Page (loginPage):
        1. New User
        2. Existing User


    New User (newUser)
        Welcome new user
            Please enter a username:
            Please enter a password:

    Existing User (existingUser)
        Welcome Old User
            Please Enter Your Username:
            Please Enter Your Password:
 
 if successfull auhtentication. Directs to Home Page
 

    Home Page (homePage)
    
    Home Page:
    
        1. Feeds
        2. Post a tweet
        3. Search People
        4. Chat
        
    Feeds
     (Yet to complete)
     
    
    Post a Tweet (postTweet)
     
     Please type your post to be tweeted.
     (After successfully receiving the tweet from client)
     
     Tweet Posted.
       1. Home Page
       2. Post Another Tweet
       3. Quit  
 
    
    Search People
      1. List of registered People
      2. Search People by name
    
    List of Regsitered People
      1. usera 
      2. user b 
      3. user c...etc
    
    user a
    Welcome to user a's home page
      1. Feeds
      2. Follow this user.
      3. List of followers
      
      
    Follow this user
      If the user already follows this person.then
      
      You have already following this person.
        1. Previous Menu
        2. Home Page
    
    else
       Successfully followed this user. 
        1. Previous Menu
        2. Home Page

'''
def extract_hash_tags(text):
    	return set([re.sub(r"#+", "", k) for k in set([re.sub(r"(\W+)$", "", j, flags = re.UNICODE) for j in set([i for i in text.split() if i.startswith("#")])])])

def sendMessage(message,client_socket):
    try:
        client_socket.send(bytes(message,'utf-8'))
    
    except:
        print("Sending Error")

def loginPage(client_socket):
    print("login Page")
    sendMessage("\n\nWelcome To Mini-Twitter \n Choose the following: \n 1. New User \n 2. Existing User\n",client_socket)
    user_response = client_socket.recv(10).decode()
    print(user_response)
    
    if user_response=='1':
        newUser(client_socket)
    elif user_response=='2':
        existingUser(client_socket)

def newUser(client_socket):
    
    
    
    
    user_database =open(USER_DATABASE, 'r+')
    user_database_dict = user_database.read()
    if len(user_database_dict)==0:
        
        
        user_to_id = open(USER_TO_ID,'r+')
        sendMessage("Welcome New User \n please enter a user name: \n",client_socket)
        user_name = client_socket.recv(30).decode()
        sendMessage("Please Enter a password: ",client_socket)
        password = client_socket.recv(30).decode()
        crypted_password = crypt.crypt(password,crypt.METHOD_SHA512)
        dictionary = {0:{'id_start':START_ID+1},START_ID+1:{'user_name':user_name,"password":crypted_password,"following":[str(START_ID+1)],"followers":[]}}
        user_database.write(json.dumps(dictionary,indent=4))
        user_id_dict ={user_name:START_ID+1}
        user_to_id.write(json.dumps(user_id_dict,indent=4))
        active_df = pd.read_csv(ACTIVE_USERS)
        active_temp = pd.DataFrame({'user_id':[START_ID+1],'active':[0]})
        active_df = active_df.append(active_temp,ignore_index=True)
        active_df.to_csv(ACTIVE_USERS,header=True,index=False)
        user_database.close()
        user_to_id.close()
            
    else:
        user_database =open(USER_DATABASE, 'r+')
        user_to_id = open(USER_TO_ID,'r+')
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
                  crypted_password = crypt.crypt(password,crypt.METHOD_SHA512)
                  
                  data[data['0']['id_start']+1]={'user_name':user_name,"password":crypted_password,"following":[str(data['0']['id_start']+1)],"followers":[]}
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
                  active_df = pd.read_csv(ACTIVE_USERS)
                  active_temp = pd.DataFrame({'user_id':[int(data['0']['id_start'])],'active':[0]})
                  active_df = active_df.append(active_temp,ignore_index=True)
                  active_df.to_csv(ACTIVE_USERS,header=True,index=False)
                  loginPage(client_socket)
                  break
                 
        print("Im here")

def feeds(client_socket,user_id):
    print("feeds")
    
    tweet_table_df = pd.read_csv(TWEET_TABLE)
    user_database =open(USER_DATABASE, 'r+')
    data =json.load(user_database)
    df = pd.DataFrame()
    for follower in data[user_id]['following']:
        print(follower)
        df = df.append(tweet_table_df[tweet_table_df['user_id']==int(follower)],ignore_index=True)

    df = df.sort_values(by='date_time_created',ascending=False )
    message=""
    for i in range(len(df)):
        user_id_temp = df.iloc[i]['user_id']
        message += f"{i+1}. {df.iloc[i]['content']} \n By : {data[str(user_id_temp)]['user_name']} \n Posted On: {df.iloc[i]['last_update_time']} \n"

    message += "\n Press 1 to go back to the home page"
    sendMessage(message,client_socket)
    response = client_socket.recv(10).decode()
    
    if response=='1':
        homePage(client_socket,user_id)
        
    
def postTweet(client_socket,user_id):
    sendMessage("Please type your tweet to be posted",client_socket)
    tweet = client_socket.recv(10000).decode()
    tweet_table_df = pd.read_csv(TWEET_TABLE)
    hash_tag_df = pd.read_csv(HASHTAG_COUNT)
    
    tweet_id = tweet_table_df.iloc[-1]['tweet_id']+1
    user_id = user_id
    date_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
    tweet_dic = {'tweet_id': [tweet_id], 'content': [tweet], 'user_id': [user_id],'date_time_created':[date_time],'last_update_time':[date_time]} 
    df_temp =pd.DataFrame(tweet_dic) 
    tweet_table_df= tweet_table_df.append(df_temp,ignore_index=True)
    tweet_table_df.to_csv(TWEET_TABLE, header=True, index=False)
    
    tweet_hashtag =open(HASHTAG, 'r+')
    hashtag_set = extract_hash_tags(tweet)
    
    if len(tweet_hashtag.read())==0:  
        
        tweet_dic_new = {}
        for item in hashtag_set:
            tweet_dic_new[item]= {'tweet_count':"1",'tweet_ids':[str(tweet_id)]}
            hash_tag_df_temp = pd.DataFrame({'hashtag':[item],'count':[1]})
            hash_tag_df =hash_tag_df.append(hash_tag_df_temp,ignore_index=True)

       
        hash_tag_df.to_csv(HASHTAG_COUNT,header=True,index=False)
        tweet_hashtag.write(json.dumps(tweet_dic_new,indent=4))
        
    
    else:
        tweet_hashtag =open(HASHTAG, 'r+')
        hashtag_dic = json.load(tweet_hashtag)
        for item in hashtag_set:
            if item in hashtag_dic.keys():
                hashtag_dic[item]['tweet_ids'].append(str(tweet_id))
                hashtag_dic[item]['tweet_count'] = int(hashtag_dic[item]['tweet_count'])+1
                hash_tag_df.loc[hash_tag_df['hashtag'] == item, ['count']] +=1
            else:
                hashtag_dic[item]={'tweet_count':"1","tweet_ids":[str(tweet_id)]}
                hash_tag_df_temp = pd.DataFrame({'hashtag':[item],'count':[1]})
                hash_tag_df =hash_tag_df.append(hash_tag_df_temp,ignore_index=True)
        
        hash_tag_df.to_csv(HASHTAG_COUNT,header=True,index=False)
        tweet_hashtag =open(HASHTAG, 'w')   
        tweet_hashtag.write(json.dumps(hashtag_dic,indent=4))
    
    tweet_hashtag.close()
    
    sendMessage("Tweet posted. \n 1. Home page. \n 2. Post Another tweet \n 3. Quit ",client_socket)
    response = client_socket.recv(30).decode()
    
    if response=='1':
        homePage(client_socket,user_id)
    elif response =='2':
       postTweet(client_socket,user_id)
    
    elif response=='3':
        logOut(client_socket) 
        
def searchByName(client_socket,user_id):
    print("search by name")


def followUser(client_socket,target_user_id,target_user_name,client_user_id):
    print("Follow this user")
    user_database =open(USER_DATABASE, 'r+')
    data =json.load(user_database)
    if target_user_id in  data[client_user_id]['following']:
        sendMessage(f"You have already following this user.\n 1. Previous Menu \n 2. Home Page \n",client_socket)
    else:
        data[client_user_id]['following'].append(target_user_id)
        data[target_user_id]['followers'].append(client_user_id)
        user_database.close()
        user_database =open(USER_DATABASE, 'w')
        user_database.write(json.dumps(data,indent=4))
        user_database.close()
        sendMessage(f"Successfully followed {target_user_name}.\n 1. Previous Menu \n 2. Home Page \n",client_socket)
    response = client_socket.recv(10).decode()
    
    if response=='1':
        individualUser(client_socket,target_user_id,target_user_name,client_user_id)
    elif response =='2':
       homePage(client_socket,client_user_id)

def viewHashtagPost(client_socket,hashtag,user_id):
    tweet_hashtag =open(HASHTAG, 'r+')
    hashtag_dic = json.load(tweet_hashtag)
    tweets_list = hashtag_dic[hashtag]['tweet_ids']
    user_database =open(USER_DATABASE, 'r+')
    data =json.load(user_database)
    tweet_table_df = pd.read_csv(TWEET_TABLE)
    message =""
    for i,item in enumerate(tweets_list):
        df_temp = tweet_table_df[tweet_table_df['tweet_id']==int(item)]
        user_id_temp = df_temp.iloc[0]['user_id']
        message += f"{i+1}. {df_temp.iloc[0]['content']} \n By : {data[str(user_id_temp)]['user_name']} \n Posted On: {df_temp.iloc[0]['last_update_time']} \n"
        
    message+= "\n To go to the home page, press 0"   
    sendMessage(message,client_socket)
    response = client_socket.recv(10).decode()
    
    if response=='0':
        homePage(client_socket,user_id) 
        

def hashtags(client_socket,user_id):
    hash_tag_df = pd.read_csv(HASHTAG_COUNT)
    hash_tag_df = hash_tag_df.sort_values(by='count',ascending=False)
    hashtag_df_temp =hash_tag_df[:5]
    
    message = ""
    for i in range(len(hashtag_df_temp)):
        message += f" {i+1} {hashtag_df_temp.iloc[i]['hashtag']} \n" 
    
    message += "To view the posts enter the respective index of the hashtag. To go to the home page, press 0"  
    sendMessage(message,client_socket)
    response = client_socket.recv(10).decode()
    
    for i in range(5):
        if response ==str(i+1):
            viewHashtagPost(client_socket,hashtag_df_temp.iloc[i]['hashtag'],user_id)
            break

    if response=='0':
        homePage(client_socket,user_id)
def listOfFollowers(client_socket,target_user_id,target_user_name,client_user_id):
    print("List of followers")
    user_database =open(USER_DATABASE, 'r+')
    data =json.load(user_database)
    user_database.close()
    message=""
    user_to_id = open(USER_TO_ID,'r+')
    user_to_id_dict = json.load(user_to_id)
    user_to_id.close()
    
    for i,item in enumerate(data[target_user_id]['followers']):
        message += f"{i+1}. {data[item]['user_name']} \n"
    
    message += "\n 0. Previous Menu "
    sendMessage(message,client_socket)  
    response = client_socket.recv(10).decode()
    
    if response=='0':
        individualUser(client_socket,target_user_id,target_user_name,client_user_id)
        sys.exit(1)
    else:
        for i,key in enumerate(user_to_id_dict.keys()):
            if response==str(i+1):
                individualUser(client_socket,user_to_id_dict[key],key,client_user_id)
                break
    
def individualUser(client_socket,target_user_id,target_user_name,client_user_id):
    print("Individual User")
    sendMessage(f"\n\nWelcome to {target_user_name}'s page. \n 1. Feeds \n 2. Follow this user. \n 3. List of followers \n0. Home Page ",client_socket)
    response = client_socket.recv(10).decode()
    print(response)
    if response=='1':
        feeds(client_socket,target_user_id)
    elif response =='2':
        print("im here.Response 2")
        followUser(client_socket,target_user_id,target_user_name,client_user_id)
    
    elif response=='3':
        listOfFollowers(client_socket,target_user_id,target_user_name,client_user_id)
    
    else:
        homePage(client_socket,client_user_id) 
    
def listOfUsers(client_socket,client_user_id):
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
            individualUser(client_socket,str(user_to_id_dict[key]),key,client_user_id)
            break

def searchPeople(client_socket,user_id):    
    print ("Search People")
    sendMessage("1. List of registered users. \n 2. Search for user by name",client_socket)
    response = client_socket.recv(30).decode()
    
    if response=='1':
        listOfUsers(client_socket,user_id)
    elif response =='2':
       searchByName(client_socket,user_id)
    
def activeUsersList(client_socket,user_id):
    
    user_database = open(USER_DATABASE,'r+')
    user_database_dict = json.load(user_database)
    follower_list = user_database_dict[user_id]['following']

    active_df = pd.read_csv(ACTIVE_USERS)
    df_new= pd.DataFrame()
    for item in follower_list:
   
        df_temp =active_df[active_df['user_id']==int(item)] #the user id is in int. active is also in int
        df_new = df_new.append(df_temp,ignore_index=True)

    df_new = df_new[df_new['active']==1]
    message ="\n\n"
    if len(df_new)>0:
        for i in range(len(df_new)):
            message += f"{i+1}. {df_new.iloc[i]['user_id']}\n"
    else:
        message += "No one is online now. Check back later"
    message += f"\n\n Press 1 to go back to previous menu, 2 for home page."
    sendMessage(message,client_socket)
    response = client_socket.recv(10).decode()
    if response=='1':
        chat(client_socket,user_id)
    elif response=='2':
        homePage(client_socket,user_id)

def chat(client_socket,user_id): 
         
    print("Chat")
    sendMessage("\n\n1. List of active users \n 2. Chat with any follower.",client_socket)
    response = client_socket.recv(10).decode()
    
    if response=='1':
        activeUsersList(client_socket,user_id)
    elif response=='2':
        print("Chat with any follower")
    else:
        homePage(client_socket,user_id)
      
def logOut(client_socket,user_id):
    print("Log out page")
    active_df = pd.read_csv(ACTIVE_USERS)
    active_df.loc[active_df['user_id']==int(user_id),['active']]=0
    active_df.to_csv(ACTIVE_USERS,header=True,index=False)
    
    sendMessage("You have been successfull Logged out.\n 1. Login Page \n 2. Quit",client_socket)
    response = client_socket.recv(30).decode()
   
    if response=='1':
        loginPage(client_socket)
    
    elif response=='2':
        client_socket.close()
             
def homePage(client_socket,user_id):
    print("Im at home page")        
    sendMessage("Home Page \n1. Feeds\n2. Post a tweet\n3. Search People\n4. Chat \n5. Trending Hashtags\n8. Logout ",client_socket)
    response = client_socket.recv(30).decode()
    
    if response=='1':
        feeds(client_socket,user_id)
    
    elif response=='2':
        postTweet(client_socket,user_id)
    
    elif response=='3':
        searchPeople(client_socket,user_id)
    
    elif response=='4':
        chat(client_socket,user_id)
    
    elif response=='5':
        hashtags(client_socket,user_id)
    
    elif response=='8':
        logOut(client_socket,user_id)            
    else:
        homePage(client_socket,user_id)
    
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
        
    #  try: 
        if compare_hash(data[str(user_to_id_dict[user_name])]['password'], crypt.crypt(password, data[str(user_to_id_dict[user_name])]['password'])): 
       
            active_df = pd.read_csv(ACTIVE_USERS)
            active_df.loc[active_df['user_id']==user_to_id_dict[user_name],['active']]=1
            active_df.to_csv(ACTIVE_USERS,header=True,index=False)
            homePage(client_socket,str(user_to_id_dict[user_name]))

            break
        else:
            sendMessage("Incorrect Password. Please re-enter correct the password",client_socket)
            password = client_socket.recv(30).decode()
            crypted_password= crypt.crypt(password,crypt.METHOD_SHA512)
                
            
  
    #  except:
    #         sendMessage("Username does not exist. Please Enter the correct username: ",client_socket)
    #         user_name = client_socket.recv(30).decode()
    
    
def persistentThread(client_socket,address):
   
    print(f"User with {address} connected")
    loginPage(client_socket)
    
        
    
    
def persistentConnection():
    
    client_socket, address = server_socket.accept()
    threading._start_new_thread(persistentThread,(client_socket,address))



print("Twitter Server Started....")
while True:
    persistentConnection()
    
    
        
    
    
    