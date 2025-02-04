import logging
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.regex import Regex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_to_mongodb(database):
    try:
        logging.info("Connecting to MongoDB")
        mongo_uri = f"mongodb+srv://{os.getenv('USER_NAME')}:{os.getenv('PASSWORD')}@cluster0.9gpef.mongodb.net/{database}?retryWrites=true&w=majority&appName=Cluster0"
        logging.info("Mongo URI: %s", mongo_uri)
        client = MongoClient(mongo_uri)
        db = client[database]
        logger.info('Connected to MongoDB')
        return True, db
    except PyMongoError as error:
        logging.critical('Error connecting to MongoDB: %s', error)
        return False, error

def create_user(collection, email, salt, pw_hash, preferences=None,  user_info=None):
    new_user = {
        "email": email,
        "salt": salt,
        "pwHash": pw_hash,
        "preferences": preferences,
        "userInfo": user_info
    }
    try:
        result = collection.insert_one(new_user)
        logger.info('User created - email: %s', email)
        return True, email
    except PyMongoError as error:
        logging.critical('Error saving package: %s', error)
        return False, error

def remove_user(email, collection):
    try:
        result = collection.delete_one({"email": email})
        logger.info('User removed: %s', email)
        return True
    except PyMongoError as error:
        logging.critical('Error removing user: %s', error)
        return False

def get_user_by_email(email, collection):
    try:
        user = collection.find_one({"email": email})
        if not user:
            logger.error('No user found with email %s', email)
            return False, None
        return True, user
    except PyMongoError as error:
        logger.error('Error fetching user: %s', error)
        return False, error
