import logging
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

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
        logging.critical('Error connecting to MongoDB: %s', error)
        return False, error

def create_user(collection, email, pw_hash, preferences=None, user_info=None):
    new_user = {
        "email": email,
        "pwHash": pw_hash,
        "preferences": preferences,
        "userInfo": user_info
    }
    try:
        result = collection.insert_one(new_user)
        logging.info('User created - email: %s', email)
        return True, email
    except PyMongoError as error:
        logging.critical('Error saving package: %s', error)
        return False, error

def remove_user(email, collection):
    try:
        result = collection.delete_one({"email": email})
        logging.info('User removed: %s', email)
        return True
    except PyMongoError as error:
        logging.critical('Error removing user: %s', error)
        return False

def get_user_by_email(email, collection):
    try:
        user = collection.find_one({"email": email})
        if not user:
            logging.info('No user found with email %s', email)
            return False, None
        return True, user
    except PyMongoError as error:
        logging.error('Error fetching user: %s', error)
        return False, error
