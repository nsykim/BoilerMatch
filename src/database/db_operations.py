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

def create_user(collection, email, pw_hash, school, preferences=empty_preferences, user_info=None):
    new_user = {
        "email": email,
        "pwHash": pw_hash,
        "school": school,
        "preferences": preferences,
        "userInfo": user_info
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
    
def remove_all_users(collection):
    try:
        result = collection.delete_many({})
        deleted_count = result.deleted_count
        logging.info('Removed %d users from the database', deleted_count)
        return True, deleted_count
    except PyMongoError as error:
        logging.error('Error removing all users: %s', error)
        return False, error

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

# FOR KNN
def get_users_by_school(school, collection, limit=100):
    try:
        # Using aggregation pipeline to first match by school then get random sample
        pipeline = [
            # Match users where userInfo.school equals the provided school
            {"$match": {"school": school}},
            # Get random sample of matched documents
            {"$sample": {"size": limit}},
            # Project only the fields we want to return
            {"$project": {
                "email": 1,
                "school": 1,
                "userInfo": 1,
                "preferences": 1,
                "_id": 0  # Exclude the MongoDB _id field
            }}
        ]
        
        users = list(collection.aggregate(pipeline))
        
        if not users:
            logging.info('No users found for school: %s', school)
            return True, []
        
        logging.info('Found %d users for school: %s', len(users), school)
        return True, users
        
    except PyMongoError as error:
        logging.error('Error fetching users by school: %s', error)
        return False, error

def update_preferences(user, preferences, collection, email):
    try:
        collection.update_one({"email": email}, {"$set": {"preferences": preferences}}) 
        user["preferences"] = preferences
        return True
    except PyMongoError as error:
        logging.error('Error updating preferences: %s', error)
        return False
    
def update_user_info(user, user_info, collection, email):
    try:
        collection.update_one({"email": email}, {"$set": {"userInfo": user_info}})
        user["userInfo"] = user_info
        return True
    except Exception as error:
        logging.error("Error updating user info: %s", error)
        return False