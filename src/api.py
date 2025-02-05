import json
import logging
from flask import Flask, request, jsonify
from accounts import *
from database.db_operations import *
import bcrypt

app = Flask(__name__)

@app.route('/create_account', methods=['POST'])
def create_account():
    body = request.json
    email = body.get('email')
    pw = body.get('password')

    if email == None or pw == None:
        logging.info("create_account: malformed request... username, email, or pw were not set")
        return '', 400
    logging.info("create_account: all required fields were set")

    success,db = connect_to_mongodb("accounts")
    table = db["accounts"]
    if (success == False):
        logging.critical("create_account: could not connect to the server")
        return '', 500
    
    success, user = get_user_by_email(email, table) # returns None if user does not exist
    if user != None:
        logging.info("create_account: email is already registered in the database")
        return '', 400
    logging.info("create_account: email address is unique")

    ### NEED TO CHECK IF PASSWORD MEETS REQUIREMENTS

    salt = bcrypt.gensalt()
    logging.info("create_account: salt generated")
    hashed_pw = bcrypt.hashpw(pw, salt)
    logging.info("create_account: password hashed: " + hashed_pw)

    success, result = create_user(table, email, salt, hashed_pw) 
    if success == True:
        logging.info("create_account: account successfully created")
        return '', 200
    else:
        logging.critical("create_account: account could not be created")
        return '', 500

    


if __name__ == '__main__':
    app.run(port=3020)