import json
import logging
from flask import Flask, request, jsonify
from accounts import *
from database.users import *

app = Flask(__name__)

@app.route('/create_account', methods=['POST'])
def create_account():
    body = request.json
    email = body.get('email')
    pw = body.get('password')
    username = body.get('username')

    if username == None and email == None and pw == None:
        logging.info("create_account: malformed request... username, email, or pw were not set")
        return jsonify({"error: not all required fields were set"}), 400
    logging.info("create_account: all required fields were set")

    user_table = get_table(client, "boilermatch", "accounts")
    if user_table == None:
        logging.critical("create_account: could not connect to user table")
        return jsonify({"error: could not connect to the server"}), 500
    logging.info("create_acocunt: successfully connected to the server")

    if search_user_db(user_table, "username", username):
        logging.info("create_account: username already exists within the database")
        return jsonify({"error: Username already exists"}), 400
    logging.info("create_account: username does not already exist in the database")

    if search_user_db(user_table, "email", email):
        logging.info("create_account: email is already registered in the database")
        return jsonify({"email address is already present within the database"}), 400
    logging.info("create_account: email address is unique")

    create_account(client, username, email, pw, None) # temporary, since need to update create_account


    


client = None
if __name__ == '__main__':
    client = connect_to_db()
    app.run(port=3020)