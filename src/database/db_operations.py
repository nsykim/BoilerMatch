import logging
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import hashlib
import time

logging.basicConfig(level=logging.INFO)
load_dotenv()

# -1 = NOT SET
# 0 = DON'T CARE / NOT IMPORTANT
# 1 = Not very important
# 2 = Somewhat important
# 3 = Very important
# 4 = Extremely important
# 5 = Deal breaker

empty_preferences = {
    "Cleanliness": -1,
    "Noise": -1,
    "Social": -1,
    "Sleep Schedule": -1,
    "Smoking": -1,
    "Pets": -1,
    "Alcohol": -1,
    "Gender": -1,
    "Age": -1,
    "Politics": -1,

}

def connect_to_mongodb(database):
    try:
        logging.info("Connecting to MongoDB")
        mongo_uri = f"mongodb+srv://{os.getenv('USER_NAME')}:{os.getenv('PW')}@boilermatch.xx9ot.mongodb.net/{database}?retryWrites=true&w=majority&appName=BoilerMatch"
        # logging.info("Mongo URI: %s", mongo_uri)
        client = MongoClient(mongo_uri)
        db = client[database]
        logging.info('Connected to MongoDB')
        return True, db
    except PyMongoError as error:
        logging.error('Error connecting to MongoDB: %s', error)
        return False, error

def create_user(collection, email, pw_hash, preferences=empty_preferences, user_info=None):
    new_user = {
        "email": email,
        "pwHash": pw_hash,
        "preferences": preferences,
        "userInfo": user_info,
        "chats": [],
        "likes": []

    }
    try:
        collection.insert_one(new_user)
        logging.info('User created - email: %s', email)
        return True, email
    except PyMongoError as error:
        logging.error('Error saving package: %s', error)
        return False, error

def remove_user(email, collection):
    try:
        result = collection.delete_one({"email": email})
        logging.info('User removed: %s', email)
        return True
    except PyMongoError as error:
        logging.error('Error removing user: %s', error)
        return False

def get_user_by_email(email, collection):
    try:
        user = collection.find_one({"email": email})
        if not user:
            logging.info('No user found with email %s', email)
            return False, None
        logging.info('User found: %s', user)
        return True, user
    except PyMongoError as error:
        logging.error('Error fetching user: %s', error)
        return False, error

def update_preferences(user, preferences, collection, email):
    try:
        collection.update_one({"email": email}, {"$set": {"preferences": preferences}}) 
        user["preferences"] = preferences
        return True
    except PyMongoError as error:
        logging.error('Error updating preferences: %s', error)
        return False

def update_chat(chat_id, collection, timetamp):
    try:
        collection.update_many(
            {"chats.chat_id": chat_id}, 
            { "$set": {
                "chats.$.lastUpdated": timetamp 
            }
        })
        return True
    except PyMongoError as error:
        logging.error('Error updating chat: %s', error)
        return False

def sort_chats(collection, email):
    try:
        user = collection.find_one({"email": email}, {"chats": {"$slice": [0, 100]}})  # Limit results
        if not user or "chats" not in user:
            logging.info('No chats found for user %s', email)
            return -1

        sorted_chats = sorted(user["chats"], key=lambda x: x.get("lastUpdated", 0), reverse=True)
        logging.info('Sorted chats for %s: %s', email, sorted_chats)
        return sorted_chats
    except PyMongoError as error:
        logging.error('Error sorting chats: %s', error)
        return None

def add_like(collection, email1, email2):
    try:
        user1 = collection.find_one({"email": email1})
        user2 = collection.find_one({"email": email2})

        if not user1 or not user2:
            logging.info('One or both users not found')
            return False, 1

        if email2 in user1.get("likes", []): # if other person already swiped on you
            logging.info('Users like eachother - match')
            return match_users(collection, email1, email2)
        
        # user2 has not already swiped on user 1, so add user1 to user2 likes
        collection.update_one({"email": email1}, {"$addToSet": {"likes": email2}})

        logging.info('Likes added for %s and %s', email1, email2)
        return True, 1
    except PyMongoError as error:
        logging.error('Error adding likes: %s', error)
        return False, error

def match_users(collection, email1, email2):
    try:
        success1, user1 = get_user_by_email(email1, collection)
        success2, user2 = get_user_by_email(email2, collection)
        if success1 == False or success2 == False:
            logging.info('Match users: one or both users not found')
            return False, -2
        logging.info('Match users: successfully retrieved both users')
        emails = sorted([email1, email2])
        chatID = hashlib.sha256("_".join(emails).encode()).hexdigest()[:16]

        if any(chat.get('chat_id') == chatID for chat in user1.get('chats', [])) or \
           any(chat.get('chat_id') == chatID for chat in user2.get('chats', [])):
            logging.info('Match users: chatID already exists')
            return False, -1
        
        logging.info('Match users: generated chatID %s', chatID)
        matchTime = int(time.time())
        user1['chats'].append({"chat_id" : chatID, "lastUpdated" : matchTime})
        user2['chats'].append({"chat_id" : chatID, "lastUpdated" : matchTime})
        try:
            collection.update_one({"email": email1}, {"$set": {"chats": user1['chats']}})
            collection.update_one({"email": email2}, {"$set": {"chats": user2['chats']}})
            logging.info('Match users: successfully updated both users')
            return True, chatID
        except PyMongoError as error:
            logging.error('Error updating users with chatID: %s', error)
            return False, error
    except PyMongoError as error:
        logging.error('Error matching users: %s', error)
        return False, error