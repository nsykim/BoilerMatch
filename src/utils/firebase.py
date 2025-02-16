import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv  
import time
import json
import os
import logging
from src.database.db_operations import update_chat

load_dotenv()

if not firebase_admin._apps: # only perform this if firebase has not been initialized
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_credentials is None: 
        logging.critical("FIREBASE_CREDENTIALS not set in .env file")
        raise ValueError("FIREBASE_CREDENTIALS not set in .env file")
    # revert credentials back into json

    firebase_credentials = json.loads(firebase_credentials)

    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def send_message(chat_id, sender, content, collection):
    timestamp = int(time.time())
    logging.info("Sending message at timestamp: %s", timestamp)
    try:
        message_ref = db.collection("chats").document(chat_id).collection("messages").document()
        message_ref.set({
            "sender": sender,
            "content": content,
            "timestamp": timestamp
        })
        logging.info("Message sent to firebase successfully")
    except Exception as e:
        logging.error("Error sending message to firebase: %s", e)
        return False
    try:
        success = update_chat(chat_id, collection, timestamp)   
        if success == False:
            logging.error("Error updating chat in mongo database")
            return False
        logging.info("Chat updated successfully in mongo")
        return True
    except Exception as e:
        logging.error("Error updating chat in mongo database: %s", e)
        return False

def fetch_chat_history(chat_id):
    try:
        messages_ref = db.collection("chats").document(chat_id).collection("messages")
        messages = messages_ref.order_by("timestamp").stream()
        chat_history = [{"id": message.id, **message.to_dict()} for message in messages]
        logging.info("Chat history fetched successfully")
        return chat_history
    except Exception as e:
        logging.error("Error fetching chat history: %s", e)
        return None