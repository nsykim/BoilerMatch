import json
import logging
from flask import Flask, request, jsonify
from database.db_operations import *
import bcrypt
from utils.jwt_utils import *
from models.roommate_recommender import RoommateRecommender
from utils.fetch_colleges import fetch_colleges

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
    school = body.get('school')

    if len(pw) < 8:
        logging.info("create_account: password is too short")
        return '', 400

    if email == None or pw == None or school == None:
        logging.info("create_account: malformed request... username, email, pw, or school were not set")
        return '', 400
    logging.info("create_account: all required fields were set")

    table = accounts_db["accounts"]

    success, user = get_user_by_email(email, table) # returns None if user does not exist
    if user != None:
        logging.info("create_account: email is already registered in the database")
        return '', 400
    logging.info("create_account: email address is unique")

    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

    success, result = create_user(table, email, hashed_pw, school) 
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
    check_hash = bcrypt.hashpw(pw.encode('utf-8'), stored_hash.encode('utf-8')).decode()
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

# FOR KNN
@app.route('/get_roommate_recommendations', methods=['GET'])
def get_roommate_recommendations():
    # Get required fields
    body = request.json
    email = body.get('email')
    session_token = request.headers['Authorization']

    if email == None:
        logging.info("login: malformed request... email not set")
        return '', 400
    logging.info("login: all required fields were set")

    if validate_jwt(session_token)['email'] != email:
        logging.info("roommate_recommendations: invalid session token")
        return session_token, 401
    logging.info("roommate_recommendations: valid session token")

    # Get target user
    table = accounts_db["accounts"]
    success, target_user = get_user_by_email(email, table)
    
    if not success or not target_user:
        return jsonify({"error": "User not found"}), 404
        
    # Get target user's school
    user_school = target_user.get("userInfo", {}).get("school")
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


accounts_db = None
chats_db = None
if __name__ == '__main__':
    success, accounts_db = connect_to_mongodb("accounts")
    if success == False:
        logging.error("could not connect to the database")
        exit(1)
    success, chats_db = connect_to_mongodb("chats")
    if success == False:
        logging.error("could not connect to the database")
        exit(1)
    app.run(port=3020, debug=True)
