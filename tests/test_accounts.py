import sys
import os
# Add the 'src' directory to sys.path so Python can find accounts.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


import unittest
from accounts import connect_to_db, get_table, create_account, update_account, delete_account, Preference
import bcrypt

# Establish a database connection
client = connect_to_db()
if client is None:
    raise ConnectionError("Failed to connect to MongoDB.")

# Get the accounts collection
accounts = get_table(client, "boilermatch", "accounts")

class TestAccountFunctions(unittest.TestCase):
    def setUp(self):
        """Set up a test account before each test."""
        self.test_account = {
            "username": "TestUser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "address": "123 Test St, Test City",  
            "preferences": {
                "cleanliness": Preference.SOMETIMES.value,
                "alcohol": Preference.RARELY.value,
            },
        }

        # Create test account and store the inserted ID
        self.inserted_id = create_account(
            client,
            self.test_account["username"],
            self.test_account["email"],
            self.test_account["password"],
            self.test_account["address"],
            preferences=self.test_account["preferences"],
        )

    def tearDown(self):
        """Clean up the test account after each test."""
        delete_account(client, self.test_account["username"])

    def test_create_account(self):
        """Test account creation and verify it exists in the database."""
        username = "TestCreate"
        email = "testcreate@example.com"
        password = "testpassword"
        address = "456 Sample Ave, Sample City"

        # Create account
        create_account(client, username, email, password, address, preferences={
            "cleanliness": Preference.OFTEN.value,
            "alcohol": Preference.NEVER.value,
        })

        # Verify the account was created in MongoDB
        created_account = accounts.find_one({"username": username})
        self.assertIsNotNone(created_account, "Account creation failed.")

        # Ensure password is stored as a hash
        self.assertIn("password_hash", created_account, "Password hash not stored.")

        # Use bcrypt to verify the stored hash matches the original password
        stored_hash = created_account["password_hash"]
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), stored_hash), "Stored password hash does not match input password.")

        # Cleanup
        delete_account(client, username)

    def test_update_account(self):
        """Test account update."""
        updates = {
            "prompt": "Updated prompt for testing.",
            "preferences.cleanliness": Preference.OFTEN.value,
        }
        matched, modified = update_account(client, self.test_account["username"], updates)

        # Verify the update
        updated_account = accounts.find_one({"username": self.test_account["username"]})

        self.assertTrue(matched, "No account matched for updating.")
        self.assertTrue(modified, "No changes were made to the account.")
        self.assertEqual(updated_account["prompt"], "Updated prompt for testing.", "Prompt update failed.")
        self.assertEqual(updated_account["preferences"]["cleanliness"], Preference.OFTEN.value, "Cleanliness preference update failed.")

    def test_delete_account(self):
        """Test account deletion."""
        delete_count = delete_account(client, self.test_account["username"])
        self.assertGreater(delete_count, 0, "Account deletion failed.")

        # Ensure account is no longer in the database
        remaining = accounts.find_one({"username": self.test_account["username"]})
        self.assertIsNone(remaining, "Account was not fully deleted.")

# Run the tests
if __name__ == "__main__":
    unittest.main()
