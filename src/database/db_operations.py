import logging
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import hashlib
import time
import hashlib
import time

#import base64
from bson.binary import Binary


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
    "age": -1,
    "alcohol": -1,
    "cleanliness": -1,
    "gender": "",
    "noise": -1,
    "hasPets": "",
    "politics": -1,
    "sleepSchedule": -1,
    "doesSmoke": "",
    "social": -1,
    "smoking_dealbreaker": -1,
    "pets_dealbreaker": -1,
    "gender_dealbreaker": -1,
}

def connect_to_mongodb(database):
    """
    Connect to MongoDB using the connection string from environment variables.

    Args:
        database (str): The name of the database to connect to.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the database object or error.
    """
    try:
        logging.info("Connecting to MongoDB")
        mongo_uri = f"mongodb+srv://{os.getenv('USER_NAME')}:{os.getenv('PW')}@boilermatch.xx9ot.mongodb.net/{database}?retryWrites=true&w=majority&appName=BoilerMatch"
        client = MongoClient(mongo_uri)
        db = client[database]
        logging.info('Connected to MongoDB')

        #for debugging
        #uri = "mongodb://localhost:27017/"  # or your Atlas URI
        print("[DEBUG] Connected to Mongo URI:", mongo_uri)
        print("[DEBUG] Using Database:", db.name)
        print("[DEBUG] Collections in DB:", db.list_collection_names())

        return True, db
    except PyMongoError as error:
        logging.error('Error connecting to MongoDB: %s', error)
        return False, error

def create_user(collection, email, pw_hash, school, preferences=empty_preferences, user_info=None):
    """
    Create a new user in the MongoDB collection.
    
    Args:
        collection: The MongoDB collection to insert the user into.
        email (str): The email of the user.
        pw_hash (str): The hashed password of the user.
        school (str): The school of the user.
        preferences (dict, optional): User preferences. Defaults to empty_preferences.
        user_info (dict, optional): Additional user information. Defaults to None.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the email or error.
    """
    new_user = {
        "email": email,
        "pwHash": pw_hash,
        "school": school,
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
    """
    Remove a user from the MongoDB collection by email.
    
    Args:
        email (str): The email of the user to remove.
        collection: The MongoDB collection to remove the user from.
        
    Returns:
        bool: True if the user was removed successfully, False otherwise.
    """
    try:
        result = collection.delete_one({"email": email})
        logging.info('User removed: %s', email)
        return True
    except PyMongoError as error:
        logging.error('Error removing user: %s', error)
        return False
    
def remove_all_users(collection):
    """
    Remove all users from the MongoDB collection.
    
    Args:
        collection: The MongoDB collection to remove users from.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the number of deleted users or error.
    """
    try:
        result = collection.delete_many({})
        deleted_count = result.deleted_count
        logging.info('Removed %d users from the database', deleted_count)
        return True, deleted_count
    except PyMongoError as error:
        logging.error('Error removing all users: %s', error)
        return False, error

def get_user_by_email(email, collection):
    """
    Fetch a user from the MongoDB collection by email.
    
    Args:
        email (str): The email of the user to fetch.
        collection: The MongoDB collection to search in.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the user document or error.
    """
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

def get_users_by_school(school, collection, limit=100):
    """
    Fetch a random sample of users from the MongoDB collection by school.
    
    Args:
        school (str): The school to filter users by.
        collection: The MongoDB collection to search in.
        limit (int): The maximum number of users to return. Defaults to 100.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the list of users or error.
    """
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
    """
    Update user preferences in the MongoDB collection.
    
    Args:
        user: The user document to update.
        preferences (dict): The new preferences to set.
        collection: The MongoDB collection to update.
        email (str): The email of the user to update.
        
    Returns:
        bool: True if the preferences were updated successfully, False otherwise.
    """
    try:
        collection.update_one({"email": email}, {"$set": {"preferences": preferences}}) 
        user["preferences"] = preferences
        return True
    except PyMongoError as error:
        logging.error('Error updating preferences: %s', error)
        return False
    
def update_user_info(user, user_info, collection, email):
    try:
         # If an image is included and it's a base64 string, convert it to Binary
        if "profile_image" in user_info and isinstance(user_info["profile_image"], bytes):
            user_info["profile_image"] = Binary(user_info["profile_image"])

        logging.info(f"profile_image present: {'profile_image' in user_info}")
        logging.info(f"profile_image type: {type(user_info.get('profile_image'))}")


        collection.update_one({"email": email}, {"$set": {"userInfo": user_info}})
        user["userInfo"] = user_info
        return True
    except Exception as error:
        logging.error("Error updating user info: %s", error)
        return False
    

def update_chat(chat_id, collection, timestamp):
    """
    Update the lastUpdated field of a chat in the MongoDB collection.
    
    Args:
        chat_id (str): The chat ID to update.
        collection: The MongoDB collection to update.
        timestamp (int): The new timestamp to set.
        
    Returns:
        bool: True if the chat was updated successfully, False otherwise.
    """
    try:
        result = collection.update_many(
            {"chats.chat_id": chat_id},
            {"$set": {"chats.$[elem].lastUpdated": timestamp}},
            array_filters=[{"elem.chat_id": chat_id}]
        )
        logging.info(f"Updated {result.modified_count} chat(s) with chat_id {chat_id}")
        return True
    except PyMongoError as error:
        logging.error('Error updating chat: %s', error)
        return False

def sort_chats(collection, email):
    """
    Sort chats for a user by lastUpdated timestamp.
    
    Args:
        collection: The MongoDB collection to search in.
        email (str): The email of the user whose chats to sort.
        
    Returns:
        list: A sorted list of chats for the user, or None if an error occurred.
    """
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
    """
    Add a like from one user to another in the MongoDB collection.
    
    Args:
        collection: The MongoDB collection to update.
        email1 (str): The email of the user who is liking.
        email2 (str): The email of the user who is being liked.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the result or error.
    """
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
        collection.update_one({"email": email2}, {"$addToSet": {"likes": email1}})

        logging.info('Likes added for %s and %s', email1, email2)
        return True, 1
    except PyMongoError as error:
        logging.error('Error adding likes: %s', error)
        return False, error

def match_users(collection, email1, email2):
    """
    Match two users by creating a chat ID and updating their chat lists.
    
    Args:
        collection: The MongoDB collection to update.
        email1 (str): The email of the first user.
        email2 (str): The email of the second user.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and the chat ID or error.
    """
    try:
        success1, user1 = get_user_by_email(email1, collection)
        success2, user2 = get_user_by_email(email2, collection)
        if not success1 or not success2:
            logging.info('Match users: one or both users not found')
            return False, -2
        logging.info('Match users: successfully retrieved both users')

        emails = sorted([email1, email2])
        chatID = hashlib.sha256("_".join(emails).encode()).hexdigest()[:16]

        # Check if chat already exists
        if any(chat.get('chat_id') == chatID for chat in user1.get('chats', [])) or \
           any(chat.get('chat_id') == chatID for chat in user2.get('chats', [])):
            logging.info('Match users: chatID already exists')
            return False, -1
        
        logging.info('Match users: generated chatID %s', chatID)
        matchTime = int(time.time())

        # Get display names
        display1 = f"{user1['userInfo'].get('userInfo').get('first_name', '')} {user1['userInfo'].get('userInfo').get('last_name', '')}".strip()
        display2 = f"{user2['userInfo'].get('userInfo').get('first_name', '')} {user2['userInfo'].get('userInfo').get('last_name', '')}".strip()

        # Add chat entry with participant info
        chat_entry1 = {
            "chat_id": chatID,
            "lastUpdated": matchTime,
            "participant": {
                "email": email2,
                "name": display2
            }
        }
        chat_entry2 = {
            "chat_id": chatID,
            "lastUpdated": matchTime,
            "participant": {
                "email": email1,
                "name": display1
            }
        }

        user1['chats'].append(chat_entry1)
        user2['chats'].append(chat_entry2)

        try:
            collection.update_one({"email": email1}, {"$set": {"chats": user1['chats']}})
            collection.update_one({"email": email2}, {"$set": {"chats": user2['chats']}})
            collection.update_one({"email": email1}, {"$pull": {"likes": email2}})
            logging.info('Match users: successfully updated both users')
            return True, chatID
        except PyMongoError as error:
            logging.error('Error updating users with chatID: %s', error)
            return False, error
    except PyMongoError as error:
        logging.error('Error matching users: %s', error)
        return False, error

def clear_mongo(collection):
    """
    Clear the specified MongoDB collection.
    
    Args:
        collection: The MongoDB collection to clear.
        
    Returns:
        bool: True if the collection was cleared successfully, False otherwise.
    """
    try:
        collection.drop()
        logging.info('Cleared collection: %s', collection.name)
        return True
    except PyMongoError as error:
        logging.error('Error clearing collection: %s', error)
        return False