import logging
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

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
        "chats": []
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
        collection.update_many({
            {"chats.chat_id": chat_id}
        }, {
            "$set": {
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
