import logging
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.regex import Regex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb(database):
    try:
        mongo_uri = f"mongodb+srv://{os.getenv('USER_NAME')}:{os.getenv('PASSWORD')}@cluster0.9gpef.mongodb.net/{database}?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(mongo_uri)
        db = client[database]
        logger.info('Connected to MongoDB')
        return True, db
    except PyMongoError as error:
        logging.critical('Error connecting to MongoDB: %s', error)
        return False, error

def add_new_package(name, url, collection, package_id=None, score=None, version=None, net_score=None, ingestion_method=None, readme=None, secret=None, user_group=None):
    new_package = {
        "name": name,
        "url": url,
        "score": score,
        "version": version,
        "packageId": package_id,
        "netScore": net_score,
        "ingestionMethod": ingestion_method,
        "README": readme,
        "secret": secret,
        "userGroup": user_group
    }
    try:
        result = collection.insert_one(new_package)
        logger.info('Package saved: %s', name)
        return True, result.inserted_id
    except PyMongoError as error:
        logging.critical('Error saving package: %s', error)
        return False, error

def remove_package_by_name_or_hash(identifier, collection):
    try:
        result = collection.delete_one({"$or": [{"name": identifier}, {"packageId": identifier}]})
        logger.info('Package removed: %s', identifier)
        return True
    except PyMongoError as error:
        logging.critical('Error removing package: %s', error)
        return False

def get_all_packages(collection):
    try:
        packages = list(collection.find())
        logger.info('All Packages: %s', packages)
        return True, packages
    except PyMongoError as error:
        logging.critical('Error fetching packages: %s', error)
        return False, error

def get_packages_by_name_or_hash(identifier, collection):
    try:
        packages = list(collection.find({"$or": [{"name": identifier}, {"packageId": identifier}]}))
        packages.sort(key=lambda x: list(map(int, x.get("version", "0").split('.'))), reverse=True)
        if not packages:
            logger.error('No packages found with the name or hash: %s', identifier)
            return False, [-1]
        return True, packages
    except PyMongoError as error:
        logger.error('Error fetching packages: %s', error)
        return False, error

def find_package_by_regex(regex, collection):
    try:
        new_regex = Regex(f'^{regex}', 'i')
        results = list(collection.find({"$or": [{"name": new_regex}, {"README": new_regex}]}))
        return True, results
    except PyMongoError as error:
        logging.critical('Error fetching packages: %s', error)
        return False, error

def delete_db(db):
    try:
        db.client.drop_database(db.name)
        logger.info('Database deleted successfully')
        return True
    except PyMongoError as error:
        logging.critical('Error deleting database: %s', error)
        return False, error


def add_user(username, user_hash, is_admin, user_group, collection):
    try:
        if collection.find_one({"username": username}):
            logger.info('User already exists')
            return False, 'User already exists'
        result = collection.insert_one({
            "username": username,
            "isAdmin": is_admin,
            "userHash": user_hash,
            "userGroup": user_group
        })
        logger.info('User added: %s', username)
        return True, result.inserted_id
    except PyMongoError as error:
        logging.critical('Error adding user: %s', error)
        return False, error

def get_user_by_name(username, collection):
    try:
        user = collection.find_one({"username": username})
        if not user:
            logger.info('User not found')
            return False, 'User not found'
        logger.info('User found: %s', user)
        return True, user
    except PyMongoError as error:
        logging.critical('Error fetching user: %s', error)
        return False, error

def remove_user_by_name(username, collection):
    try:
        if not collection.find_one({"username": username}):
            logger.info('User does not exist')
            return False, 'User does not exist'
        result = collection.delete_one({"username": username})
        logger.info('User removed: %s', username)
        return True, result.deleted_count
    except PyMongoError as error:
        logging.critical('Error removing user: %s', error)
        return False, error
