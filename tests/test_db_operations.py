import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock the entire MongoDB client before importing the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

with patch('pymongo.MongoClient'):
    from database.db_operations import (
        connect_to_mongodb,
        create_user,
        remove_user,
        get_user_by_email,
        update_preferences,
        get_users_by_school
    )

from pymongo.errors import PyMongoError

class TestDatabaseOperations(unittest.TestCase):
    @patch.dict(os.environ, {
        "USER_NAME": "test_user",
       "PW": "test_password"
    })

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up environment variables
        self.env_patcher = patch.dict(os.environ, {
            "USER_NAME": "test_user",
            "PW": "test_password"
        })
        self.env_patcher.start()

        # Create the base mocks
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_client = MagicMock()
        
        # Configure mock returns
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection

        # Start MongoDB client patcher
        self.mongo_patcher = patch('database.db_operations.MongoClient', return_value=self.mock_client)
        self.mock_mongo_client = self.mongo_patcher.start()

        # Import after patching
        global connect_to_mongodb, create_user, remove_user, get_user_by_email, get_users_by_school
        from database.db_operations import (
            connect_to_mongodb,
            create_user,
            remove_user,
            get_user_by_email,
            get_users_by_school
        )

    def tearDown(self):
        """Clean up after each test"""
        self.env_patcher.stop()
        self.mongo_patcher.stop()

    def test_connect_to_mongodb_success(self):
        """Test successful MongoDB connection."""
        # Reset mock in case it was modified by other tests
        self.mock_mongo_client.reset_mock()
        self.mock_mongo_client.return_value = self.mock_client
        
        success, db = connect_to_mongodb("test_db")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(db, self.mock_db)
        self.mock_mongo_client.assert_called_once()
        
        # Verify connection string
        connection_string = self.mock_mongo_client.call_args[0][0]
        self.assertIn("test_user", connection_string)
        self.assertIn("test_password", connection_string)
        self.assertIn("test_db", connection_string)

    def test_connect_to_mongodb_failure(self):
        """Test MongoDB connection failure."""
        # Configure mock to raise exception
        self.mock_mongo_client.reset_mock()
        self.mock_mongo_client.side_effect = PyMongoError("Connection failed")
        
        success, error = connect_to_mongodb("test_db")
        
        # Assertions
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)
        self.assertEqual(str(error), "Connection failed")
        
        # Reset side effect for other tests
        self.mock_mongo_client.side_effect = None
        self.mock_mongo_client.return_value = self.mock_client


    def test_create_user_success(self):
        """Test successful user creation."""
        # Test data
        email = "test@example.com"
        pw_hash = "test_hash"
        school = "Purdue University"
        
        # Configure mock
        self.mock_collection.insert_one.return_value.inserted_id = "123"
        
        # Execute test
        success, result = create_user(self.mock_collection, email, pw_hash, school)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(result, email)
        self.mock_collection.insert_one.assert_called_once()
        
        # Verify the document structure
        called_doc = self.mock_collection.insert_one.call_args[0][0]
        self.assertEqual(called_doc["email"], email)
        self.assertEqual(called_doc["pwHash"], pw_hash)

    def test_create_user_with_optional_fields(self):
        """Test user creation with preferences and user info."""
        # Test data
        email = "test@example.com"
        pw_hash = "test_hash"
        school = "IU"
        preferences = {"theme": "dark"}
        user_info = {"name": "Test User"}
        
        # Execute test
        success, result = create_user(
            self.mock_collection,
            email,
            pw_hash,
            school,
            preferences=preferences,
            user_info=user_info
        )
        
        # Assertions
        self.assertTrue(success)
        called_doc = self.mock_collection.insert_one.call_args[0][0]
        self.assertEqual(called_doc["preferences"], preferences)
        self.assertEqual(called_doc["userInfo"], user_info)

    def test_create_user_failure(self):
        """Test user creation failure."""
        # Configure mock to raise exception
        self.mock_collection.insert_one.side_effect = PyMongoError("Insert failed")
        
        # Execute test
        success, error = create_user(self.mock_collection, "test@example.com", "salt", "hash")
        
        # Assertions
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)
        self.assertEqual(str(error), "Insert failed")

    def test_remove_user_success(self):
        """Test successful user removal."""
        # Configure mock
        self.mock_collection.delete_one.return_value.deleted_count = 1
        
        # Execute test
        success = remove_user("test@example.com", self.mock_collection)
        
        # Assertions
        self.assertTrue(success)
        self.mock_collection.delete_one.assert_called_once_with({"email": "test@example.com"})

    def test_remove_user_failure(self):
        """Test user removal failure."""
        # Configure mock to raise exception
        self.mock_collection.delete_one.side_effect = PyMongoError("Delete failed")
        
        # Execute test
        success = remove_user("test@example.com", self.mock_collection)
        
        # Assertions
        self.assertFalse(success)

    def test_get_user_by_email_success(self):
        """Test successful user retrieval."""
        # Test data
        expected_user = {
            "email": "test@example.com",
            "pwHash": "test_hash",
            "preferences": None,
            "userInfo": None
        }
        
        # Configure mock
        self.mock_collection.find_one.return_value = expected_user
        
        # Execute test
        success, user = get_user_by_email("test@example.com", self.mock_collection)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(user, expected_user)
        self.mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})

    def test_get_user_by_email_not_found(self):
        """Test user retrieval when user doesn't exist."""
        # Configure mock
        self.mock_collection.find_one.return_value = None
        
        # Execute test
        success, user = get_user_by_email("test@example.com", self.mock_collection)
        
        # Assertions
        self.assertFalse(success)
        self.assertIsNone(user)

    def test_get_user_by_email_failure(self):
        """Test user retrieval failure."""
        # Configure mock to raise exception
        self.mock_collection.find_one.side_effect = PyMongoError("Find failed")
        
        # Execute test
        success, error = get_user_by_email("test@example.com", self.mock_collection)
        
        # Assertions
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)
        self.assertEqual(str(error), "Find failed")

    def test_get_users_by_school_success(self):
        """Test successful retrieval of users by school."""
        # Test data
        test_users = [
            {
                "email": "user1@test.com",
                "userInfo": {"school": "Purdue"},
                "preferences": {"Cleanliness": 3}
            },
            {
                "email": "user2@test.com",
                "userInfo": {"school": "Purdue"},
                "preferences": {"Cleanliness": 4}
            },
            {
                "email": "user3@test.com",
                "userInfo": {"school": "IU"},
                "preferences": {"Cleanliness": 5}
            }
        ]
        
        # Configure mock to return test data
        self.mock_collection.aggregate.return_value = test_users[:2]  # Only Purdue users
        
        # Execute test
        success, users = get_users_by_school("Purdue", self.mock_collection)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["email"], "user1@test.com")
        self.assertEqual(users[1]["email"], "user2@test.com")
        
        # Verify the aggregation pipeline
        pipeline_arg = self.mock_collection.aggregate.call_args[0][0]
        self.assertEqual(len(pipeline_arg), 3)  # Match, Sample, and Project stages
        self.assertEqual(pipeline_arg[0]["$match"], {"userInfo.school": "Purdue"})
        self.assertEqual(pipeline_arg[1]["$sample"], {"size": 100})  # Default limit
        self.assertEqual(pipeline_arg[2]["$project"], {
            "email": 1,
            "userInfo": 1,
            "preferences": 1,
            "_id": 0
        })

    def test_get_users_by_school_custom_limit(self):
        """Test getting users by school with custom limit."""
        # Configure mock
        self.mock_collection.aggregate.return_value = []
        
        # Execute test
        success, users = get_users_by_school("Purdue", self.mock_collection, limit=50)
        
        # Verify the limit in aggregation pipeline
        pipeline_arg = self.mock_collection.aggregate.call_args[0][0]
        self.assertEqual(pipeline_arg[1]["$sample"], {"size": 50})

    def test_get_users_by_school_empty_result(self):
        """Test when no users are found for a school."""
        # Configure mock to return empty list
        self.mock_collection.aggregate.return_value = []
        
        # Execute test
        success, users = get_users_by_school("NonexistentSchool", self.mock_collection)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(len(users), 0)

    def test_get_users_by_school_failure(self):
        """Test handling of database errors."""
        # Configure mock to raise exception
        self.mock_collection.aggregate.side_effect = PyMongoError("Aggregation failed")
        
        # Execute test
        success, error = get_users_by_school("Purdue", self.mock_collection)
        
        # Assertions
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)
        self.assertEqual(str(error), "Aggregation failed")

    def test_update_preferences_success(self):
        # Configure mock for successful preferences update
        user = {
            "email": "test@example.com",
            "preferences": {
                "Cleanliness": -1,
                "Noise": -1,
                "Social": -1,
                "Sleep Schedule": -1,
                "Smoking": -1,
                "Pets": -1,
                "Alcohol": -1,
                "Gender": -1,
                "Age": -1,
                "Politics": -1,
            }
        }
        new_preferences = {
            "Cleanliness": 3,
            "Noise": 2,
            "Social": 4,
            "Sleep Schedule": 1,
            "Smoking": 0,
            "Pets": 5,
            "Alcohol": 2,
            "Gender": 1,
            "Age": 3,
            "Politics": 4,
        }
        
        success = update_preferences(user, new_preferences, self.mock_collection, "test@example.com")
        
        self.assertTrue(success)
        self.assertEqual(user["preferences"], new_preferences)
        self.mock_collection.update_one.assert_called_once_with(
            {"email": "test@example.com"},
            {"$set": {"preferences": new_preferences}}
        )

    def test_update_preferences_failure(self):
        # Simulate database error during preferences update
        user = {
            "email": "test@example.com",
            "preferences": {
                "Cleanliness": -1,
                "Noise": -1,
                "Social": -1,
                "Sleep Schedule": -1,
                "Smoking": -1,
                "Pets": -1,
                "Alcohol": -1,
                "Gender": -1,
                "Age": -1,
                "Politics": -1,
            }
        }
        new_preferences = {
            "Cleanliness": 3,
            "Noise": 2,
            "Social": 4,
            "Sleep Schedule": 1,
            "Smoking": 0,
            "Pets": 5,
            "Alcohol": 2,
            "Gender": 1,
            "Age": 3,
            "Politics": 4,
        }
        self.mock_collection.update_one.side_effect = PyMongoError("Update failed")
        
        success = update_preferences(user, new_preferences, self.mock_collection, "test@example.com")
        
        self.assertFalse(success)
        self.assertNotEqual(user["preferences"], new_preferences)

if __name__ == "__main__":
  unittest.main()