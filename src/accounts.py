import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from enum import Enum
from dotenv import load_dotenv
import bcrypt
import logging

def connect_to_db():
    # Load environment variables
    load_dotenv()
    # Get credentials from .env file
    MONGO_USERNAME = os.getenv("MONGO_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

    #Connect to Mongo DB
    uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@boilermatch.xx9ot.mongodb.net/?retryWrites=true&w=majority&appName=BoilerMatch"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        logging.info("connect_to_db: Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        logging.critical(e)

    # Database and collection
    return client
    
def get_table(client, db_name, table_name):
    if client is None:
        logging.critical("get_table: Client is not connected. Call connect_to_db() first.")
        return None
    logging.info("get_table: successfully connected to {table_name} table")
    db = client[db_name]
    return db[table_name] #RETURN THIS to use later



# Enum for preferences
class Preference(Enum):
    NOT_SPECIFIED = 0
    NEVER = 1
    RARELY = 2
    SOMETIMES = 3
    OFTEN = 4

##ACCOUNT CREATION
def create_account(client, username, email, password, address, images=None, prompt=None, preferences=None):
    """Creates a new user account in MongoDB."""
    accounts = get_table(client, "boilermatch", "accounts")

    # Hash the password with bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    account = {
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "salt": salt,
        "address": address,
        "images": images if images else [""] * 3,
        "prompt": prompt if prompt else "No prompt provided.",
        "preferences": {
            "cleanliness": Preference.NOT_SPECIFIED.value,
            "alcohol": Preference.NOT_SPECIFIED.value,
            "marijuana": Preference.NOT_SPECIFIED.value,
            "smoking": Preference.NOT_SPECIFIED.value,
            **(preferences or {})
        },
    }

    # Insert into MongoDB
    result = accounts.insert_one(account)
    logging.info(f"✅ Account created successfully with ID: {result.inserted_id}")
    return result.inserted_id


##DELETE FUNCTION
# Function to delete an account by username
#returns 0 if error
def delete_account(client, username):
    """Deletes a user account from MongoDB."""
    accounts = get_table(client, "boilermatch", "accounts")

    try:
        result = accounts.delete_one({"username": username})
        
        if result.deleted_count > 0:
            logging.info(f"✅ Account '{username}' deleted successfully.")
        else:
            logging.info(f"❌ No account found with username '{username}'.")
        
        return result.deleted_count
    except Exception as e:
        logging.critical(f"❌ Error deleting account: {e}")
        return 0



# Function to update an account by username
def update_account(client, identifier, updates):
    """Updates an existing user account in MongoDB."""
    accounts = get_table(client, "boilermatch", "accounts")

    try:
        result = accounts.update_one({"$or": [{"username": identifier}, {"email": identifier}]}, {"$set": updates})

        matched = result.matched_count > 0
        modified = result.modified_count > 0

        if matched:
            logging.info(f"✅ Account '{identifier}' found.")
            if modified:
                logging.info(f"✅ Account '{identifier}' updated successfully.")
            else:
                logging.info(f"ℹ️ No changes were made to account '{identifier}'.")
        else:
            logging.info(f"❌ No account found with identifier '{identifier}'.")

        return matched, modified
    except Exception as e:
        logging.critical(f"❌ Error updating account: {e}")
        return False, False
