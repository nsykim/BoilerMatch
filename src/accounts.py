import os
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from enum import Enum
from dotenv import load_dotenv
import bcrypt
import logging
import re
# Function to update an account by username
# returns true/false based on success
import logging
from pymongo import MongoClient

#Pass in username, password, app_name
#output is client, true/false
# client points to db or is None if failed
# true if success
# false if failed
def connect_to_db(username, password, app_name="BoilerMatch"):
    """Establishes a connection to the MongoDB database using credentials from environment variables."""
    
    if not username or not password:
        logging.critical("connect_to_db: MongoDB credentials are missing.")
        return None, False

    # Connect to MongoDB
    uri = f"mongodb+srv://{username}:{password}@boilermatch.xx9ot.mongodb.net/?retryWrites=true&w=majority&appName={app_name}"
    
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        logging.info("connect_to_db: Successfully connected to MongoDB.")
        return client, True
    except Exception as e:
        logging.critical(f"connect_to_db: Connection failed - {e}")
        return None, False

#Pass in client, db_name, table_name
# MAKE SURE CLIENT IS RESULT OF CONNECT_TO_DB
#output is table, true/false
# table points to table or is None if failed
# true if success
# false if failed
def get_table(client, db_name, table_name):
    if client is None:
        logging.critical("get_table: Client is not connected. Call connect_to_db() first.")
        return None, False

    try: 
        db = client[db_name]
        collection = db[table_name]
        logging.info(f"get_table: Successfully connected to '{table_name}' table in database '{db_name}'.")
        return collection, True
    except Exception as e:
        logging.critical(f"get_table: Failed to retrieve table '{table_name}' - {e}")
        return None, False

def is_valid_email(email):
    """Checks if an email is valid."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None

# Enum for likert preferences
class Preference(Enum):
    NOT_SPECIFIED = 0
    NEVER = 1
    RARELY = 2
    DONT_CARE = 3 
    SOMETIMES = 4
    OFTEN = 5

# Enum for user specified weights/dealbreakers
class IsDealbreaker(Enum):
    NOT_DEALBREAKER = False #DEFAULT
    DEALBEAKER = True

class AccessLevel(Enum):
    ADMIN = 0 
    USER = 1 #DEFAULT

##ACCOUNT CREATION
# client: MongoDB client from connect_to_db().
# email (str): User's email.
# username: maybe used or not
# password (str): User's password.
# name_on_profile (str): Display name for the profile.
# images (list, optional): List of image URLs.
# prompt (str, optional): User's profile prompt.
# preferences (dict, optional): User's internal preferences as (value, dealbreaker).


#returns inserted_id
# returns true/false based on success
def create_account(client, username, email, password, name_on_profile, address, access_level = AccessLevel.USER.value, images=None, prompt=None, preferences=None):
    """Creates a new user account in MongoDB."""
    users, success = get_table(client, "boilermatch", "accounts")
    if not success:
        logging.error("create_account: ❌ could not access accounts table.")
        return None, False

    #check valid email
    if not is_valid_email(email):
        logging.error("create_account: ❌ Invalid email format.")
        return None, False
    
    #check valid new user
    existing_user = users.find_one({"email": email})
    if existing_user:
        logging.error(f"create_account: ❌ Account with email '{email}' already exists.")
        return None, False
    
    #check valid access level
    if access_level not in [level.value for level in AccessLevel]:
        logging.error(f"create_account: ❌ Invalid access level '{access_level}'.")
        return None, False

    # Hash the password with bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    default_preferences = { #theres an argumentr that should be set like this IF YOU WANT TO SET PREFERENCES at account creation
        "cleanliness": {"value": Preference.NOT_SPECIFIED.value, "dealbreaker": False},
        "alcohol": {"value": Preference.NOT_SPECIFIED.value, "dealbreaker": False},
        "marijuana": {"value": Preference.NOT_SPECIFIED.value, "dealbreaker": False},
        "smoking": {"value": Preference.NOT_SPECIFIED.value, "dealbreaker": False},
        "sleep_schedule": {"value": Preference.NOT_SPECIFIED.value, "dealbreaker": False},
        "social": {"value": Preference.NOT_SPECIFIED.value, "dealbreaker": False},
    }
    # Merge provided preferences while keeping defaults
    preferences = default_preferences | (preferences or {})

    account = {
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "salt": salt,
        "access_level": access_level,
        
        "user_info": {
            "name_on_profile": name_on_profile,
            "address": address,
            "images": images if images else [""] * 3,
            "prompt": prompt if prompt else "No prompt provided."
        },

        "preferences": preferences
    }

    # Insert into MongoDB
    try:
        result = users.insert_one(account)
        logging.info(f"create_account: ✅ Account created successfully with ID: {result.inserted_id}")
        return result.inserted_id, True
    except pymongo.errors.WriteError as e:
        logging.critical(f"create_account: ❌ MongoDB schema validation error: {e}")
        return None, False
    except Exception as e:
        logging.critical(f"create_account: ❌ Account creation failed - {e}")
        return None, False

##DELETE FUNCTION
# Function to delete an account by email
#returns false if error, true if success
def delete_account(client, email):

    if not is_valid_email(email):
        logging.critical("delete_account: ❌ Invalid email format.")
        return False

    """Deletes a user account from MongoDB."""
    accounts, success = get_table(client, "boilermatch", "accounts")
    if not success:
        logging.critical("delete_account: ❌ Failed to connect to accounts table.")
        return False

    try:
        result = accounts.delete_one({"email": email})
        
        if result.deleted_count > 0:
            logging.info(f"✅ Account with email '{email}' deleted successfully.")
            return True
        else:
            logging.info(f"delete_account: ❌ No account found with email '{email}'.")
            return False

    except Exception as e:
        logging.critical(f"delete_account: ❌ Error deleting account: {e}")
        return False

def update_account_preferences(client, email, updates):
    """Updates an existing user account in MongoDB."""
    accounts, success = get_table(client, "boilermatch", "accounts")
    if not success:
        logging.critical("update_account: ❌ Failed to connect to accounts table.")
        return False

    if not updates:
        logging.info("update_account: ℹ️ No updates provided.")
        return False

    # Convert nested dictionary structure to dot notation for MongoDB
    update_dict = {}
    for key, value in updates.items():
        if isinstance(value, dict):  # Handle nested dictionaries
            for sub_key, sub_value in value.items():
                update_dict[f"preferences.{key}.{sub_key}"] = sub_value
        else:
            update_dict[f"preferences.{key}"] = value

    try:
        result = accounts.update_one({"email": email}, {"$set": update_dict})

        if result.matched_count == 0:
            logging.info(f"update_account: ❌ No account found with email '{email}'.")
            return False

        if result.modified_count > 0:
            logging.info(f"update_account: ✅ Account '{email}' updated successfully.")
            logging.info(f"update_account: 🔄 Updated fields: {list(update_dict.keys())}")
            return True
        else:
            logging.info(f"update_account: ℹ️ No changes were made to account '{email}'.")
            return False

    except Exception as e:
        logging.critical(f"update_account: ❌ Error updating account: {e}")
        return False


#schema to create accounts. THIS WILL DELETE ALL NON-COMPLIANT ACCOUNTS
def create_accounts_collection(client):
    """Creates the accounts collection with schema validation."""
    db = client["boilermatch"]

    # Dynamically fetch allowed access levels from the AccessLevel Enum
    access_level_values = [level.value for level in AccessLevel]

    # Dynamically fetch allowed preference names from the Preference Enum
    preference_names = [p.name.lower() for p in Preference]  # Converts enum names to lowercase

    # Generate the preferences schema dynamically
    preferences_schema = {
        pref: {
            "bsonType": "object",
            "required": ["value", "dealbreaker"],
            "properties": {
                "value": {
                    "bsonType": "int",
                    "minimum": min(Preference._value2member_map_),  # Lowest enum value
                    "maximum": max(Preference._value2member_map_),  # Highest enum value
                    "description": f"Value must be between {min(Preference._value2member_map_)} and {max(Preference._value2member_map_)}."
                },
                "dealbreaker": {
                    "bsonType": "bool",
                    "description": "Indicates whether this preference is a dealbreaker."
                }
            }
        }
        for pref in preference_names
    }

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["username", "email", "password_hash", "salt", "access_level", "user_info", "preferences"],
            "properties": {
                "username": {
                    "bsonType": "string",
                    "minLength": 3,
                    "description": "Username must be at least 3 characters long."
                },
                "email": {
                    "bsonType": "string",
                    "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
                    "description": "Must be a valid email address."
                },
                "password_hash": {
                    "bsonType": "binData",
                    "description": "Password hash stored as binary data."
                },
                "salt": {
                    "bsonType": "binData",
                    "description": "Salt used for password hashing."
                },
                "access_level": {
                    "bsonType": "int",
                    "enum": access_level_values,  # Dynamically allows all AccessLevel values
                    "description": f"Must be one of {access_level_values}."
                },
                "user_info": {
                    "bsonType": "object",
                    "required": ["name_on_profile", "address"],
                    "properties": {
                        "name_on_profile": {
                            "bsonType": "string",
                            "description": "User's display name."
                        },
                        "address": {
                            "bsonType": "string",
                            "description": "User's address."
                        },
                        "images": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"},
                            "description": "List of image URLs."
                        },
                        "prompt": {
                            "bsonType": "string",
                            "description": "User's profile prompt."
                        }
                    }
                },
                "preferences": {
                    "bsonType": "object",
                    "description": "User preferences stored as key-value pairs.",
                    "properties": preferences_schema  # Uses dynamically generated preference schema
                }
            }
        }
    }

    try:
        db.create_collection("accounts", validator=schema)
        print("✅ 'accounts' collection created successfully with schema validation.")
        return True
    except Exception as e:
        print(f"❌ Error creating 'accounts' collection: {e}")
        return False


#add helpers for insert one to catch exceptions or fails
#make functions return true on success, false on failure
#make accounts fit account schema in text
#update tests to be done in one testing file easily
#make a file that has test_db_main or something and import shit