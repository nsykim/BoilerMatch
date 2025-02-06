import json
import logging
from flask import Flask, request, jsonify
from accounts import *
from database.db_operations import *
import bcrypt

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


    hashed_pw = bcrypt.hash_pw(pw, bcrypt.gensalt(log_rounds=12))
    logging.info("create_account: password hashed: " + hashed_pw)

    success, result = create_user(table, email, hashed_pw) 
    if success == True:
        logging.info("create_account: account successfully created")
        return '', 200
    else:
        logging.critical("create_account: account could not be created")
        return '', 500

    

@app.route('/login', methods=['POST'])
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


    success, user = get_user_by_email(email, table)
    if success == False:
        logging.info("login: error fetching user")
        return '', 500
    elif user == None:
        logging.info("login: user not found")
        return '', 400

    if bcrypt.check_pw(pw, user['pwHash']):
        logging.info("login: password matches")
        ## need to return JWT token
        return '', 200
    else: 
        logging.info("login: password does not match")
        return '', 400



accounts_db = None
chats_db = None
if __name__ == '__main__':
    success, accounts_db = connect_to_mongodb("accounts")
    if success == False:
        logging.critical("could not connect to the database")
        exit(1)
    success, chats_db = connect_to_mongodb("chats")
    if success == False:
        logging.critical("could not connect to the database")
        exit(1)
    app.run(port=3020)