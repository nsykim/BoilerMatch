from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from enum import Enum

#PASSWORD HASHING LATER

#Connect to Mongo DB
uri = "mongodb+srv://admin:WQOzlLwi1fM68V1e@boilermatch.xx9ot.mongodb.net/?retryWrites=true&w=majority&appName=BoilerMatch"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Database and collection
db = client["boilermatch"]
accounts = db["accounts"]



# Enum for preferences
class Preference(Enum):
    NOT_SPECIFIED = 0
    NEVER = 1
    RARELY = 2
    SOMETIMES = 3
    OFTEN = 4

##ACCOUNT CREATION
# Create an account function
def create_account(
    username,
    email,
    password,
    images=None,  # images
    prompt=None,  # prompt
    preferences=None  # Optional preferences
):
    # Incorporate default values
    account = {
        "username": username,
        "email": email,
        "password": password,
        "images": images if images else [""] * 3,  # Default to 3 empty strings
        "prompt": prompt if prompt else "No prompt provided.",  # Default prompt
        "preferences": {
            "cleanliness": Preference.NOT_SPECIFIED.value,
            "alcohol": Preference.NOT_SPECIFIED.value,
            "marijuana": Preference.NOT_SPECIFIED.value,
            "smoking": Preference.NOT_SPECIFIED.value,
            **(preferences or {})  # Merge user-specified preferences
        },
    }
    # Insert the document into the collection
    result = accounts.insert_one(account)
    print(f"Account created successfully with ID: {result.inserted_id}")


##DELETE FUNCTION
# Function to delete an account by username
def delete_account(username):
    try:
        # Delete the document with the specified username
        result = accounts.delete_one({"username": username})
        
        # Check if the account was deleted
        if result.deleted_count > 0:
            print(f"Account '{username}' deleted successfully.")
        else:
            print(f"No account found with username '{username}'.")
    except Exception as e:
        print(f"An error occurred while deleting the account: {e}")



# Function to update an account by username
def update_account(username, updates):
    try:
        # Update the account document with the provided updates
        result = accounts.update_one({"username": username}, {"$set": updates})
        
        # Check if the account was updated
        if result.matched_count > 0:
            if result.modified_count > 0:
                print(f"Account '{username}' updated successfully.")
            else:
                print(f"Account '{username}' found, but no changes were made.")
        else:
            print(f"No account found with username '{username}'.")
    except Exception as e:
        print(f"An error occurred while updating the account: {e}")