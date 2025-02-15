import json
import logging
from flask import Flask, request, jsonify
from database.db_operations import *
import bcrypt
from utils.jwt_utils import *
from utils.fetch_colleges import fetch_colleges
from utils.firebase import *

app = Flask(__name__)

@app.route('/delete_account/<email>', methods=['DELETE'])
def delete_account(email):
    # TEMPORARY FUNCTION FOR TESTING PURPOSES
    table = accounts_db["accounts"]
    success = remove_user(email, table)
    if success == True:
        return '', 200
    else:
        return '', 500

@app.route('/create_account', methods=['POST'])
def create_account():
    body = request.json
    email = body.get('email')
    pw = body.get('password')

    if len(pw) < 8:
        logging.info("create_account: password is too short")
        return '', 400

    if email == None or pw == None:
        logging.info("create_account: malformed request... username, email, or pw were not set")
        return '', 400
    logging.info("create_account: all required fields were set")

    table = accounts_db["accounts"]

    success, user = get_user_by_email(email, table) # returns None if user does not exist
    if user != None:
        logging.info("create_account: email is already registered in the database")
        return '', 400
    logging.info("create_account: email address is unique")


    hashed_pw = bcrypt.hashpw(pw, bcrypt.gensalt(log_rounds=12))

    success, result = create_user(table, email, hashed_pw) 
    if success == True:
        logging.info("create_account: account successfully created")
        return '', 200
    else:
        logging.error("create_account: account could not be created")
        return '', 500

    

@app.route('/login', methods=['GET'])
def login():
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
    check_hash = bcrypt.hashpw(pw, stored_hash)
    if stored_hash == check_hash: # check if passwords match. do this because bcrypt.checkpw is not working... temporary i hope
        logging.info("login: password matches")
        return jsonify({"session_token": generate_jwt(user["email"])}), 200
    else: 
        logging.info("login: password does not match")
        return '', 400
    
@app.route('/autocomplete_colleges', methods=['GET'])
def autocomplete_colleges():
    query = request.args.get('q', '').strip()
    result, status_code = fetch_colleges(query)
    
    if isinstance(result, dict): # Error case
        return jsonify(result), status_code
    
    return jsonify({"colleges": result}), status_code


@app.route('/set_preferences', methods=['POST'])
def set_preferences():
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
        return session_token, 200
    else:
        logging.error("set_preferences: preferences could not be updated")
        return session_token, 500

@app.route('/get_user_info', methods=['POST'])
def get_user_info():
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
    return jsonify(user), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    body = request.json
    chat_id = body.get('chat_id') # frontend needs to get chat_id based on who they are texting
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
    if send_message(chat_id, email, content, table):
        logging.info("send_message: message sent successfully")
        return '', 200
    else:
        logging.error("send_message: message could not be sent")
        return '', 500
    

@app.route('/open_chat', methods=['POST'])
def open_chat():
    body = request.json
    chat_id = body.get('chat_id')
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
    app.run(port=3020)
