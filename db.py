from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from werkzeug.security import check_password_hash
from user import User
import cnode
client = MongoClient('mongodb+srv://DS-name:DSChat@dschatapp.i0dxy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

chat_db = client.get_database("DSChatDB")
users_collection = chat_db.get_collection("users")
messages_collection = chat_db.get_collection("messages")
chats_collection = chat_db.get_collection("chats")




def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email':email, 'password': password_hash })



def get_user(username):
    user_data = users_collection.find_one({'_id':username})
    return(User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None)

def check_password(self,password):
    return(check_password_hash(self.password, password))

def save_chat(sender, receiver, text):
    chats_collection.insert_one({'sender': sender, 'receiver': receiver, 'text': text, 'created_at': datetime.now()})

def retrieve_chat(sender):
    chats = chats_collection.find({"$or":[{'sender': sender},{'receiver': sender}]})
    return chats
    