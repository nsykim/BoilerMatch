import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pymongo.errors import PyMongoError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from database.db_operations import connect_to_mongodb, create_user, remove_user, get_user_by_email

class TestDatabaseOperations(unittest.TestCase):
    
    @patch("database.db_operations.MongoClient")
    @patch.dict(os.environ, {"USER_NAME": "test_user", "PASSWORD": "test_pass"})
    def test_connect_to_mongodb_success(self, mock_mongo_client):
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = MagicMock()
        
        success, db = connect_to_mongodb("test_db")
        
        self.assertTrue(success)
        self.assertIsNotNone(db)

    @patch("database.db_operations.MongoClient", side_effect=PyMongoError("Connection failed"))
    @patch.dict(os.environ, {"USER_NAME": "test_user", "PASSWORD": "test_pass"})
    def test_connect_to_mongodb_failure(self, mock_mongo_client):
        success, error = connect_to_mongodb("test_db")
        
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)

    def test_create_user_success(self):
        mock_collection = MagicMock()
        mock_collection.insert_one.return_value.inserted_id = "12345"
        
        success, result = create_user(mock_collection, "test_email", "test_salt", "test_password")
        
        self.assertTrue(success)
        self.assertEqual(result, "test_email")

    def test_create_user_failure(self):
        mock_collection = MagicMock()
        mock_collection.insert_one.side_effect = PyMongoError("Insertion failed")
        
        success, error = create_user(mock_collection, "test_email", "test_salt", "test_password")
        
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)

    def test_get_user_by_email_success(self):
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"email": "test_email"}
        
        success, user = get_user_by_email("test_email", mock_collection)
        
        self.assertTrue(success)
        self.assertEqual(user["email"], "test_email")

    def test_get_user_by_email_not_found(self):
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        
        success, user = get_user_by_email("test_email", mock_collection)
        
        self.assertFalse(success)
        self.assertIsNone(user)

    def test_get_user_by_email_failure(self):
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = PyMongoError("Query failed")
        
        success, error = get_user_by_email("test_email", mock_collection)
        
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)

    def test_remove_user_success(self):
        mock_collection = MagicMock()
        mock_collection.delete_one.return_value.deleted_count = 1
        
        success = remove_user("test_email", mock_collection)
        
        self.assertTrue(success)

    def test_remove_user_failure(self):
        mock_collection = MagicMock()
        mock_collection.delete_one.side_effect = PyMongoError("Deletion failed")
        
        success = remove_user("test_email", mock_collection)
        
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()