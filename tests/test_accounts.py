import sys
import os
# Add the 'src' directory to sys.path so Python can find accounts.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest
from accounts import connect_to_db, get_table, create_account, create_accounts_collection, update_account_preferences, delete_account
from accounts import Preference, IsDealbreaker #need this for TESTING, and if you want to use those enums
from dotenv import load_dotenv

class TestAccounts(unittest.TestCase):
    """Unit test framework for MongoDB account operations."""

    @classmethod
    def setUpClass(cls):
        """Set up resources before running any tests."""
        cls.client = client
        cls.accounts = accounts

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests are done."""
        cls.client.close()

    def setUp(self):
        """Run before each test. Creates test account data."""
        self.test_email = "test_user@example.com"
        self.test_username = "testuser"
        self.test_password = "password123"
        self.test_name = "Test User"
        self.test_address = "123 Test St"
        #test account credentials

    def tearDown(self):
        """Run after each test."""
        delete_account(self.client, self.test_email)

    def test_create_valid_account1(self):
            """Test creating a valid account."""
            inserted_id, success = create_account(
                self.client,
                self.test_username,
                self.test_email,
                self.test_password,
                self.test_name,
                self.test_address
            )

            # Ensure the account creation was successful
            self.assertTrue(success, "test_create_valid_account1: ❌ Account creation failed when it should have succeeded.")
            self.assertIsNotNone(inserted_id, "test_create_valid_account1: ❌ Inserted ID should not be None for a valid account.")

            # Verify the account exists in the database
            created_account = self.accounts.find_one({"email": self.test_email})
            self.assertIsNotNone(created_account, "test_create_valid_account1: ❌ The account was not found in the database after creation.")
            self.assertEqual(created_account["email"], self.test_email, "test_create_valid_account1: ❌ Email mismatch in the created account.")
            self.assertEqual(created_account["username"], self.test_username, "test_create_valid_account1: ❌ Username mismatch in the created account.")

    def test_create_account_invalid_email(self):
        """Test creating an account with an invalid email format."""
        invalid_email = "invalid-email"  # No @ symbol

        inserted_id, success = create_account(
            self.client,
            self.test_username,
            invalid_email,
            self.test_password,
            self.test_name,
            self.test_address
        )

        self.assertFalse(success, "❌ Account creation should have failed due to invalid email format.")
        self.assertIsNone(inserted_id, "❌ Inserted ID should be None for an invalid email.")

    def test_create_account_duplicate_email(self):
        """Test creating an account with an already existing email."""
        # First, create a valid account
        inserted_id, success = create_account(
            self.client,
            self.test_username,
            self.test_email,
            self.test_password,
            self.test_name,
            self.test_address
        )
        
        self.assertTrue(success, "❌ First account creation should have succeeded.")
        self.assertIsNotNone(inserted_id, "❌ Inserted ID should not be None for the first valid account.")

        # Attempt to create another account with the same email
        inserted_id_dup, success_dup = create_account(
            self.client,
            "newuser",  # Different username
            self.test_email,  # Same email as before
            "newpassword123",
            "New User",
            "456 Another St"
        )

        self.assertFalse(success_dup, "❌ Account creation should have failed due to duplicate email.")
        self.assertIsNone(inserted_id_dup, "❌ Inserted ID should be None for a duplicate email.")

    def test_delete_existing_account(self):
        """Test deleting an existing account."""
        # First, create a valid account
        inserted_id, success = create_account(
            self.client,
            self.test_username,
            self.test_email,
            self.test_password,
            self.test_name,
            self.test_address
        )

        self.assertTrue(success, "❌ First account creation should have succeeded.")
        self.assertIsNotNone(inserted_id, "❌ Inserted ID should not be None for the valid account.")

        # Ensure the account exists before deletion
        created_account = self.accounts.find_one({"email": self.test_email})
        self.assertIsNotNone(created_account, "❌ The account should exist before deletion.")

        # Attempt to delete the account
        delete_success = delete_account(self.client, self.test_email)

        self.assertTrue(delete_success, "❌ Account deletion should have succeeded.")

        # Ensure the account no longer exists
        deleted_account = self.accounts.find_one({"email": self.test_email})
        self.assertIsNone(deleted_account, "❌ The account should not exist after deletion.")

    def test_delete_account_invalid_email(self):
        """Test deleting an account with an invalid email format."""
        invalid_email = "invalid-email"  # No '@' symbol

        # Attempt to delete an account with an invalid email
        delete_success = delete_account(self.client, invalid_email)

        self.assertFalse(delete_success, "❌ Account deletion should have failed due to invalid email format.")

    def test_delete_non_existent_account(self):
        """Test deleting an account that does not exist."""
        non_existent_email = "doesnotexist@example.com"

        # Attempt to delete an account that doesn't exist
        delete_success = delete_account(self.client, non_existent_email)

        self.assertFalse(delete_success, "❌ Account deletion should have failed because the account does not exist.")

    def test_update_account_preferences(self):
        """Test updating an account's preferences."""
        # First, create a valid account
        inserted_id, success = create_account(
            self.client,
            self.test_username,
            self.test_email,
            self.test_password,
            self.test_name,
            self.test_address
        )

        self.assertTrue(success, "❌ Account creation should have succeeded.")
        self.assertIsNotNone(inserted_id, "❌ Inserted ID should not be None for a valid account.")

        # Define new preferences to update
        new_preferences = {
            "cleanliness": {"value": Preference.OFTEN.value, "dealbreaker": True},
            "alcohol": {"value": Preference.NEVER.value, "dealbreaker": False},
        }

        # Attempt to update the account's preferences
        update_success = update_account_preferences(self.client, self.test_email, new_preferences)

        self.assertTrue(update_success, "❌ Account preference update should have succeeded.")

        # Fetch the updated account
        updated_account = self.accounts.find_one({"email": self.test_email})
        
        self.assertIsNotNone(updated_account, "❌ The account should exist after updating preferences.")
        self.assertEqual(updated_account["preferences"]["cleanliness"]["value"], Preference.OFTEN.value, "❌ Cleanliness preference update failed.")
        self.assertEqual(updated_account["preferences"]["cleanliness"]["dealbreaker"], True, "❌ Cleanliness dealbreaker update failed.")
        self.assertEqual(updated_account["preferences"]["alcohol"]["value"], Preference.NEVER.value, "❌ Alcohol preference update failed.")
        self.assertEqual(updated_account["preferences"]["alcohol"]["dealbreaker"], False, "❌ Alcohol dealbreaker update failed.")

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Extract MongoDB credentials
    MONGO_USERNAME = os.getenv("MONGO_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")
    MONGO_APPNAME = os.getenv("MONGO_APPNAME")


    # Establish a database connection
    client, success = connect_to_db(MONGO_USERNAME, MONGO_PASSWORD)
    if not success:
        raise ConnectionError("Failed to connect to MongoDB.")

    # Get the accounts collection
    accounts, success = get_table(client, "boilermatch", "accounts")
    if not success:
        raise ConnectionError("❌ Failed to access 'accounts' collection.")

    #set the account_collection schema
    create_accounts_collection(client)

    unittest.main()
