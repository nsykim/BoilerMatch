import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import hashlib
import hashlib

# Mock the entire MongoDB client before importing the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

with patch('pymongo.MongoClient'):
    from database.db_operations import (
        connect_to_mongodb,
        create_user,
        remove_user,
        get_user_by_email,
        update_preferences,
        sort_chats,
        update_chat,
        add_like,
        match_users,
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
                "school": "Purdue",
                "preferences": {"Cleanliness": 3}
            },
            {
                "email": "user2@test.com",
                "school": "Purdue",
                "preferences": {"Cleanliness": 4}
            },
            {
                "email": "user3@test.com",
                "school": "IU",
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
        self.assertEqual(pipeline_arg[0]["$match"], {"school": "Purdue"})
        self.assertEqual(pipeline_arg[1]["$sample"], {"size": 100})  # Default limit
        self.assertEqual(pipeline_arg[2]["$project"], {
            "email": 1,
            "userInfo": 1,
            "school": 1,
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

    def test_update_chat_success(self):
        """Test successful chat update."""
        # Configure mock
        chat_id = "test_chat_123"
        timestamp = 1234567890
        self.mock_collection.update_many.return_value.modified_count = 1
        
        # Execute test
        success = update_chat(chat_id, self.mock_collection, timestamp)
        
        # Assertions
        self.assertTrue(success)
        self.mock_collection.update_many.assert_called_once_with(
            {"chats.chat_id": chat_id},
            {"$set": {"chats.$[elem].lastUpdated": timestamp}},
            array_filters=[{"elem.chat_id": chat_id}]
        )

    def test_update_chat_failure(self):
        """Test chat update failure due to database error."""
        # Configure mock to raise exception
        chat_id = "test_chat_123"
        timestamp = 1234567890
        self.mock_collection.update_many.side_effect = PyMongoError("Update failed")
        
        # Execute test
        success = update_chat(chat_id, self.mock_collection, timestamp)
        
        # Assertions
        self.assertFalse(success)

    def test_sort_chats_success(self):
        """Test successful chat sorting."""
        # Test data
        email = "test@example.com"
        test_chats = [
            {"chat_id": "chat1", "lastUpdated": 1000},
            {"chat_id": "chat2", "lastUpdated": 3000},
            {"chat_id": "chat3", "lastUpdated": 2000}
        ]
        mock_user = {"email": email, "chats": test_chats}
        
        # Configure mock
        self.mock_collection.find_one.return_value = mock_user
        
        # Execute test
        result = sort_chats(self.mock_collection, email)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["chat_id"], "chat2")  # Most recent first
        self.assertEqual(result[1]["chat_id"], "chat3")
        self.assertEqual(result[2]["chat_id"], "chat1")
        self.mock_collection.find_one.assert_called_once_with(
            {"email": email},
            {"chats": {"$slice": [0, 100]}}
        )

    def test_sort_chats_no_chats(self):
        """Test sorting when user has no chats."""
        # Configure mock to return user without chats
        self.mock_collection.find_one.return_value = {"email": "test@example.com"}
        
        # Execute test
        result = sort_chats(self.mock_collection, "test@example.com")
        
        # Assertions
        self.assertEqual(result, -1)

    def test_sort_chats_user_not_found(self):
        """Test sorting when user doesn't exist."""
        # Configure mock to return None (user not found)
        self.mock_collection.find_one.return_value = None
        
        # Execute test
        result = sort_chats(self.mock_collection, "test@example.com")
        
        # Assertions
        self.assertEqual(result, -1)

    def test_sort_chats_failure(self):
        """Test sorting failure due to database error."""
        # Configure mock to raise exception
        self.mock_collection.find_one.side_effect = PyMongoError("Find failed")
        
        # Execute test
        result = sort_chats(self.mock_collection, "test@example.com")
        
        # Assertions
        self.assertIsNone(result)

    def test_match_users_success(self):
        """Test successful matching of two users."""
        # Test data
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Configure mocks
        self.mock_collection.find_one.side_effect = [
            {"email": email1, "chats": [], "userInfo": {"first_name": "test1", "last_name": "1"}},
            {"email": email2, "chats": [], "userInfo": {"first_name": "test2", "last_name": "2"}}
        ]
        
        # Configure get_user_by_email mock returns
        with patch('database.db_operations.get_user_by_email') as mock_get_user:
            mock_get_user.side_effect = [
                (True, {"email": email1, "chats": [], "userInfo": {"first_name": "test1", "last_name": "1"}}),
                (True, {"email": email2, "chats": [], "userInfo": {"first_name": "test2", "last_name": "2"}})
            ]
            
            # Execute test
            success, chat_id = match_users(self.mock_collection, email1, email2)
            
            # Assertions
            self.assertTrue(success)
            self.assertIsInstance(chat_id, str)
            self.assertEqual(len(chat_id), 16)
            
            # Verify update_one calls
            self.assertEqual(self.mock_collection.update_one.call_count, 3)
            
            calls = self.mock_collection.update_one.call_args_list
            
            # Verify first update call
            first_call = calls[0]
            self.assertEqual(first_call[0][0], {"email": email1})
            self.assertIn("chats", first_call[0][1]["$set"])
            self.assertEqual(len(first_call[0][1]["$set"]["chats"]), 1)
            
            # Verify second update call
            second_call = calls[1]
            self.assertEqual(second_call[0][0], {"email": email2})
            self.assertIn("chats", second_call[0][1]["$set"])
            self.assertEqual(len(second_call[0][1]["$set"]["chats"]), 1)
            
            # Verify same chat ID
            chat1 = first_call[0][1]["$set"]["chats"][0]["chat_id"]
            chat2 = second_call[0][1]["$set"]["chats"][0]["chat_id"]
            self.assertEqual(chat1, chat2)

    def test_match_users_consistent_chat_id(self):
        """Test that the same pair of users always gets the same chat ID."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        with patch('database.db_operations.get_user_by_email') as mock_get_user:
            # First match
            mock_get_user.side_effect = [
                (True, {"email": email1, "chats": [], "userInfo": {"first_name": "test1", "last_name": "1"}}),
                (True, {"email": email2, "chats": [], "userInfo": {"first_name": "test2", "last_name": "2"}})
            ]
            success1, chat_id1 = match_users(self.mock_collection, email1, email2)
            
            # Reset mock for second match
            self.mock_collection.reset_mock()
            mock_get_user.side_effect = [
                (True, {"email": email2, "chats": [], "userInfo": {"first_name": "test1", "last_name": "1"}}),
                (True, {"email": email1, "chats": [], "userInfo": {"first_name": "test2", "last_name": "2"}})
            ]
            success2, chat_id2 = match_users(self.mock_collection, email2, email1)
            
            # Assertions
            self.assertTrue(success1)
            self.assertTrue(success2)
            self.assertEqual(chat_id1, chat_id2)

    def test_match_users_existing_chat(self):
        """Test matching users when chat already exists."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Sort emails to match the function's chat ID generation
        emails = sorted([email1, email2])
        expected_chat_id = hashlib.sha256("_".join(emails).encode()).hexdigest()[:16]
        
        with patch('database.db_operations.get_user_by_email') as mock_get_user:
            mock_get_user.side_effect = [
                (True, {"email": email1, "chats": [{"chat_id": expected_chat_id, "lastUpdated": 1000}], "userInfo": {"first_name": "test1", "last_name": "1"}}),
                (True, {"email": email2, "chats": [], "userInfo": {"first_name": "test2", "last_name": "2"}})
            ]
            
            success, result = match_users(self.mock_collection, email1, email2)
            
            self.assertFalse(success)
            self.assertEqual(result, -1)
            self.mock_collection.update_one.assert_not_called()

    def test_match_users_get_user_failure(self):
        """Test matching failure when unable to retrieve users."""
        with patch('database.db_operations.get_user_by_email') as mock_get_user:
            mock_get_user.return_value = (False, PyMongoError("Failed to retrieve user"))
            
            success, error = match_users(self.mock_collection, "test1@example.com", "test2@example.com")
            
            self.assertFalse(success)
            self.assertEqual(error,  -2)
            self.mock_collection.update_one.assert_not_called()

    def test_match_users_update_failure(self):
        """Test matching failure when unable to update users."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        with patch('database.db_operations.get_user_by_email') as mock_get_user:
            mock_get_user.side_effect = [
                (True, {"email": email1, "chats": [], "userInfo": {"first_name": "test1", "last_name": "1"}}),
                (True, {"email": email2, "chats": [], "userInfo": {"first_name": "test2", "last_name": "2"}})
            ]
            
            self.mock_collection.update_one.side_effect = PyMongoError("Failed to update user")
            
            success, error = match_users(self.mock_collection, email1, email2)
            
            self.assertFalse(success)
            self.assertIsInstance(error, PyMongoError)
            self.assertEqual(str(error), "Failed to update user")

    def test_add_like_success(self):
        """Test successful addition of a like when there's no mutual like."""
        # Test data
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Configure mocks
        self.mock_collection.find_one.side_effect = [
            {"email": email1, "likes": []},  # user1
            {"email": email2, "likes": []}   # user2
        ]
        
        # Execute test
        success, result = add_like(self.mock_collection, email1, email2)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(result, 1)
        self.mock_collection.update_one.assert_called_once_with(
            {"email": email2},
            {"$addToSet": {"likes": email1}}
        )

    def test_add_like_mutual_match(self):
        """Test when adding a like results in a mutual match."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        expected_chat_id = hashlib.sha256("_".join(sorted([email1, email2])).encode()).hexdigest()[:16]
        
        # Configure mocks for initial like check
        self.mock_collection.find_one.side_effect = [
            {"email": email1, "likes": [email2]},
            {"email": email2, "likes": []}
        ]
        
        # Mock match_users at the correct import level
        with patch('database.db_operations.match_users', return_value=(True, expected_chat_id)):
            # Import the function after patching
            from database.db_operations import add_like
            
            # Execute test
            success, result = add_like(self.mock_collection, email1, email2)
            
            # Assertions
            self.assertTrue(success)
            self.assertEqual(result, expected_chat_id)
            self.assertEqual(len(result), 16)


    def test_add_like_user_not_found(self):
        """Test when one of the users doesn't exist."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Configure mock to return None for user2
        self.mock_collection.find_one.side_effect = [
            {"email": email1, "likes": []},
            None
        ]
        
        # Execute test
        success, result = add_like(self.mock_collection, email1, email2)
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(result, 1)
        self.mock_collection.update_one.assert_not_called()

    def test_add_like_database_error(self):
        """Test handling of database errors during like addition."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Configure mocks
        self.mock_collection.find_one.side_effect = [
            {"email": email1, "likes": []},
            {"email": email2, "likes": []}
        ]
        self.mock_collection.update_one.side_effect = PyMongoError("Update failed")
        
        # Execute test
        success, error = add_like(self.mock_collection, email1, email2)
        
        # Assertions
        self.assertFalse(success)
        self.assertIsInstance(error, PyMongoError)
        self.assertEqual(str(error), "Update failed")

    def test_add_like_empty_likes_array(self):
        """Test adding a like when the likes array doesn't exist yet."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        
        # Configure mocks - user1 doesn't have a likes array yet
        self.mock_collection.find_one.side_effect = [
            {"email": email1},  # No likes array
            {"email": email2, "likes": []}
        ]
        
        # Execute test
        success, result = add_like(self.mock_collection, email1, email2)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(result, 1)
        self.mock_collection.update_one.assert_called_once_with(
            {"email": email2},
            {"$addToSet": {"likes": email1}}
        )

if __name__ == "__main__":
  unittest.main()