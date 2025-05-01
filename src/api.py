import json
import logging
from flask import Flask, request, jsonify
from database.db_operations import *
import bcrypt
from utils.jwt_utils import *
from models.roommate_recommender import RoommateRecommender
from utils.fetch_colleges import fetch_colleges
import time
from utils.firebase import *
import hashlib
from flask_cors import CORS

import base64
import re


app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # CHANGE WHEN IN PROD
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

### 
@app.route('/delete_account/<email>', methods=['DELETE'])
def delete_account(email):
    """
    TEMPORARY FUNCTION FOR TESTING PURPOSES
    Deletes the account with the given email address from the MongoDB.

    Requires:
    - email: The email address of the account to delete in the URL.

    Return Codes:
    - 200: Account deleted successfully.
    - 500: Error deleting account.
    """
    table = accounts_db["accounts"]
    success = remove_user(email, table)
    if success == True:
        return '', 200
    else:
        return '', 500

@app.route('/create_account', methods=['POST'])
def create_account():
    """
    Creates a new account in the MongoDB.

    Requires:
    - email: The email address of the account to create in the body.
    - password: The password of the account to create in the body.
    - school: The school of the account to create in the body.

    Return Codes:
    - 200: Account created successfully.
    - 400: Malformed request or email already registered.
    - 500: Error creating account.
    """
    body = request.json
    email = body.get('email')
    pw = body.get('password')
    school = body.get('school')

    logging.info(f"email: {email}")
    logging.info(f"password: {pw}")
    logging.info(f"school: {school}")

    if len(pw) < 8:
        logging.info("create_account: password is too short")
        return '', 400

    if email == None or pw == None or school == None:
        logging.info("create_account: malformed request... username, email, pw, or school were not set")
        return '', 400
    logging.info("create_account: all required fields were set")

    table = accounts_db["accounts"]

    success, user = get_user_by_email(email, table)
    if user != None:
        logging.info("create_account: email is already registered in the database")
        return '', 400
    logging.info("create_account: email address is unique")

    hashed_pw = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(log_rounds=12))

    success, result = create_user(table, email, hashed_pw, school) 
    if success == True:
        logging.info("create_account: account successfully created")
        return jsonify({"message": "account success"}), 200
    else:
        logging.error("create_account: account could not be created")
        return '', 500

@app.route('/login', methods=['POST'])
def login():
    """
    Logs in a user and returns a session token to allow access to other app functionality.

    Requires:
    - email: The email address of the account to log in in the body.
    - password: The password of the account to log in in the body.

    Return Codes:
    - 200: Login successful, returns session token.
    - 400: Malformed request or invalid email/password.
    - 500: Error logging in.
    """
    body = request.json
    email = body.get('email')
    pw = body.get('password')

    if email == None or pw == None:
        logging.info("login: malformed request... username, email, or pw were not set")
        return '', 400
    logging.info("login: all required fields were set")

    table = accounts_db["accounts"]

    success, user = get_user_by_email(email, table)
    if success == False:
        logging.info("login: error fetching user")
        return '', 500
    elif user == None:
        logging.info("login: user not found")
        return '', 400

    stored_hash = user["pwHash"]
    check_hash = bcrypt.hashpw(pw.encode("utf-8"), stored_hash)
    if stored_hash == check_hash: # check if passwords match. do this because bcrypt.checkpw is not working... temporary i hope
        logging.info("login: password matches")
        return jsonify({"session_token": generate_jwt(user["email"])}), 200
    else: 
        logging.info("login: password does not match")
        return '', 400
    
@app.route('/autocomplete_colleges', methods=['GET'])
def autocomplete_colleges():
    """
    Autocompletes college names based on a user-typed query.

    Requires:
    - q: A query string in the URL parameters (e.g., /autocomplete_colleges?q=berk).
    - session_token: The session token of the user in the Authorization header.

    Return Codes:
    - 200: Successfully returned a list of matching colleges.
    - 500: Error retrieving college suggestions.
    """

    query = request.args.get('q', '').strip()
    result, status_code = fetch_colleges(query)

    if isinstance(result, dict):
        return jsonify(result), status_code

    return jsonify({"colleges": result}), status_code

@app.route('/get_roommate_recommendations', methods=['POST'])
def get_roommate_recommendations():
    """
    Gets roommate recommendations for a user based on their preferences and school.

    Requires:
    - email: The email address of the account to get recommendations for in the body.
    - session_token: The session token of the user in the headers.

    Return Codes:
    - 200: Recommendations successfully retrieved.
    - 400: Malformed request or invalid session token.
    - 401: Unauthorized access.
    - 404: User not found.
    - 500: Error retrieving recommendations.
    """
    body = request.json
    email = body.get('email')
    session_token = request.headers['Authorization']

    if email == None:
        logging.info("login: malformed request... email not set")
        return '', 400
    logging.info("login: all required fields were set")

    if validate_jwt(session_token)['email'] != email:
        logging.info("roommate_recommendations: invalid session token")
        return jsonify({"error": "Unauthorized"}), 401
    logging.info("roommate_recommendations: valid session token")
    
    # Get target user
    table = accounts_db["accounts"]
    success, target_user = get_user_by_email(email, table)
    
    if not success or not target_user:
        return jsonify({"error": "User not found"}), 404
        
    # Get target user's school
    user_school = target_user.get("school")
    if not user_school:
        return jsonify({"error": "User school not found"}), 400
        
    # Get potential matches from same school
    success, school_users = get_users_by_school(user_school, table)
    if not success:
        return jsonify({"error": "Failed to fetch potential matches"}), 500
        
    # Initialize recommender and get recommendations
    recommender = RoommateRecommender(n_neighbors=20)
    recommendations = recommender.get_recommendations(target_user, school_users)
    
    # Format and return recommendations
    formatted_recommendations = recommender.format_recommendations(recommendations)
    
    return jsonify({
        "recommendations": formatted_recommendations
    }), 200

@app.route('/set_preferences', methods=['POST'])
def set_preferences():
    """
    Sets the preferences for a user in the MongoDB.

    Requires:
    - email: The email address of the account to set preferences for in the body.
    - session_token: The session token of the user in the headers.
    - preferences: The preferences to set for the user in the body.

    Return Codes:
    - 200: Preferences successfully updated.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 500: Error updating preferences.
    """
    body = request.json
    email = body.get('email')
    session_token = request.headers['Authorization']
    preferences = body.get('preferences')

    if email == None or session_token == None or preferences == None:
        logging.info("set_preferences: malformed request... username, email, or pw were not set")
        return session_token, 400
    logging.info("set_preferences: all required fields were set")

    if validate_jwt(session_token)['email'] != email:
        logging.info("set_preferences: invalid session token")
        return session_token, 401
    logging.info("set_preferences: valid session token")

    table = accounts_db["accounts"]

    success, user = get_user_by_email(email, table)
    if success == False or user == None:
        logging.info("set_preferences: error fetching user")
        return session_token, 500
    
    logging.info("user: %s", user)
    success = update_preferences(user, preferences, table, email)
    if success == True:
        logging.info("set_preferences: preferences successfully updated")
        return jsonify({"message": "Preferences successfully updated"}), 200
    else:
        logging.error("set_preferences: preferences could not be updated")
        return session_token, 500

@app.route('/set_user_info', methods=['POST'])
def set_user_info():
    """
    Sets the user info for a user in the MongoDB.
    
    Requires:
    - email: The email address of the account to set user info for in the body.
    - session_token: The session token of the user in the headers.
    - user_info: The user info to set for the user in the body.
    
    Return Codes:
    - 200: User info successfully updated.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 500: Error updating user info.
    """
    body = request.json
    email = body.get('email')
    session_token = request.headers.get('Authorization')
    user_info = body.get('user_info')
    
    if not email or not session_token or not user_info:
        logging.info("set_user_info: malformed request... missing email, session token, or user_info")
        return session_token, 400
    logging.info("set_user_info: all required fields were set")
    
    if validate_jwt(session_token)['email'] != email:
        logging.info("set_user_info: invalid session token")
        return session_token, 401
    logging.info("set_user_info: valid session token")
    
    table = accounts_db["accounts"]
    success, user = get_user_by_email(email, table)
    if not success or user is None:
        logging.info("set_user_info: error fetching user")
        return session_token, 500
    
    #FOR IMAGE UPLOAODING
    # 👇 Decode base64 profile image string if present
    # ✅ Do not decode — keep profile_image as a string
    logging.info("set_user_info: storing profile image as-is")
    
    logging.info("User found: %s", user)
    success = update_user_info(user, user_info, table, email)
    if success:
        logging.info("set_user_info: user info successfully updated")
        return jsonify({"message": "User info successfully updated"}), 200
    else:
        logging.error("set_user_info: user info could not be updated")
        return session_token, 500

@app.route('/get_user_info', methods=['POST'])
def get_user_info():
    """
    Gets the user info for a user in the MongoDB.
    
    Requires:
    - email: The email address of the account to get user info for in the body.
    - session_token: The session token of the user in the headers.
    
    Return Codes:
    - 200: User info successfully retrieved.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 500: Error retrieving user info.
    """
    body = request.json
    email = body.get('email')
    session_token = request.headers['Authorization']

    if email == None or session_token == None:
        logging.info("get_user_info: malformed request... username, email, or pw were not set")
        return session_token, 400
    logging.info("get_user_info: all required fields were set")

    if validate_jwt(session_token)['email'] != email:
        logging.info("get_user_info: invalid session token")
        return session_token, 401
    logging.info("get_user_info: valid session token")

    table = accounts_db["accounts"]

    success, user = get_user_by_email(email, table)
    if success == False or user == None:
        logging.info("get_user_info: error fetching user")
        return session_token, 500
    
    logging.info("user: %s", user)
    user["_id"] = str(user["_id"])
    return jsonify(user), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Sends a message to a chat via Firebase Firestore and updates metadata in the MongoDB.
    
    Requires:
    - chat_id: The ID of the chat to send the message to in the headers.
    - session_token: The session token of the user in the headers.
    - email: The email address of the user sending the message in the body.
    - content: The content of the message to send in the body.

    Return Codes:
    - 200: Message sent successfully.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 500: Error sending message.
    """
    body = request.json
    chat_id = request.headers['chat_id']
    content = body.get('content')
    session_token = request.headers['Authorization']
    email = body.get('email')

    if chat_id == None or content == None or email == None:
        logging.info("send_message: malformed request... chat_id, content, or email were not set")
        return '', 400
    logging.info("send_message: all required fields were set") 

    if validate_jwt(session_token)['email'] != email:
        logging.info("send_message: invalid session token")
        return session_token, 401
    logging.info("send_message: valid session token")

    table = accounts_db["accounts"]
    if fb_send_message(chat_id, email, content, table):
        logging.info("send_message: message sent successfully")
        return '', 200
    else:
        logging.error("send_message: message could not be sent")
        return '', 500
    
@app.route('/open_chat', methods=['POST'])
def open_chat():
    """
    Opens a chat and retrieves the chat history from Firebase Firestore.
    
    Requires:
    - chat_id: The ID of the chat to open in the headers.
    - session_token: The session token of the user in the headers.
    - email: The email address of the user opening the chat in the body.
    
    Return Codes:
    - 200: Chat history retrieved successfully.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 500: Error retrieving chat history.
    """
    body = request.json
    chat_id = request.headers['chat_id']
    session_token = request.headers['Authorization']
    email = body.get('email')

    if chat_id == None or email == None:
        logging.info("open_chat: malformed request... chat_id, content, or email were not set")
        return '', 400
    logging.info("open_chat: all required fields were set") 

    if validate_jwt(session_token)['email'] != email:
        logging.info("open_chat: invalid session token")
        return session_token, 401
    logging.info("open_chat: valid session token")

    chat_history = fetch_chat_history(chat_id)
    
    if chat_history == None:
        logging.error("open_chat: error fetching chat history")
        return '', 500
    logging.info("open_chat: chat history fetched successfully")

    return jsonify(chat_history), 200

@app.route('/chats_page', methods=['POST'])
def chats_page():
    """
    Retrieves the chats for a user and sorts them by last message time.
    
    Requires:
    - email: The email address of the user to retrieve chats for in the body.
    - session_token: The session token of the user in the headers.
    
    Return Codes:
    - 200: Chats retrieved and sorted successfully.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 500: Error retrieving or sorting chats.
    """
    body = request.json
    email = body.get('email')
    session_token = request.headers['Authorization']

    if email == None:
        logging.info("chats_page: malformed request... email was not set")
        return '', 400
    logging.info("chats_page: all required fields were set")

    if validate_jwt(session_token)['email'] != email:
        logging.info("chats_page: invalid session token")
        return '', 401
    logging.info("chats_page: valid session token")

    table = accounts_db["accounts"]
    
    sorted_chats = sort_chats(table, email)
    if sorted_chats == None:
        logging.info("chats_page: error retrieving or sorting chats")
        return '', 500
    elif sorted_chats == -1:
        logging.info("chats_page: no chats found")
        return None, 200
    else:
        logging.info("chats_page: chats sorted successfully")
        return jsonify(sorted_chats), 200


@app.route('/like', methods=['POST'])
def like():
    """
    Likes a user and creates a chat if both users have liked each other.
    
    Requires:
    - email: The email address of the user liking another user in the body.
    - other: The email address of the user to be liked in the body.
    - session_token: The session token of the user in the headers.

    Return Codes:
    - 200: Like added successfully or chat created.
    - 400: Malformed request or missing fields.
    - 401: Unauthorized access.
    - 403: Users have already been matched.
    - 500: Error adding like or creating chat. 
    """
    body = request.json
    email = body.get('email')
    other = body.get('other')    
    session_token = request.headers['Authorization']

    if email == None:
        logging.info("match: malformed request... email was not set")
        return '', 400
    logging.info("match: all required fields were set")

    if validate_jwt(session_token)['email'] != email:
        logging.info("match: invalid session token")
        return session_token, 401
    logging.info("match: valid session token")

    table = accounts_db["accounts"]
    success, id = add_like(table, email, other)
    if success == False and (id == 1 or id == -2):
        logging.info("match: error fetching user")
        return '', 500
    elif success == False and id == -1:
        logging.info("match: users have already been matched")
        return '', 403
    elif success == False and type(id) == PyMongoError:
        logging.info("match: error matching users")
        return '', 500
    elif success == True and id == 1:
        logging.info("match: added like onto %s", other)
        return jsonify({"message": "Like added."}), 200
    elif success == True:
        logging.info("match: users matched")
        return jsonify({"chat_id" : id}), 200

@app.route('/clear_db', methods=['DELETE'])
def clear_db():
    """
    TEMPORARY FUNCTION FOR TESTING PURPOSES
    Clears the MongoDB database by deleting all accounts and chats.
    
    Return Codes:
    - 200: Database cleared successfully.
    - 500: Error clearing database.
    """


    try:
        success = clear_mongo(accounts_db["accounts"])
        if success == False:
            logging.error("Error clearing accounts database")
            return '', 500
        success = delete_chats_collection() 
        if success == False:
            logging.error("Error clearing chats database")
            return '', 500  
    except Exception as e:
        logging.error("Error clearing database: %s", e)
        return '', 500

    if success == True:
        return '', 200
    else:
        return '', 500

accounts_db = None
if __name__ == '__main__':
    success, accounts_db = connect_to_mongodb("accounts")
    if success == False:
        logging.error("could not connect to the database")
        exit(1)
    success, chats_db = connect_to_mongodb("chats")
    if success == False:
        logging.error("could not connect to the database")
        exit(1)
    app.run(host="0.0.0.0", port=3020, debug=True)