import unittest
from accounts import create_account, update_account, delete_account, Preference
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#Connect to Mongo DB
uri = "mongodb+srv://<MitchelCraven>:<BeanBurrito>@boilermatch.xx9ot.mongodb.net/?retryWrites=true&w=majority&appName=BoilerMatch"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Database and collection
db = client["boilermatch"]
accounts = db["accounts"]

class TestAccountFunctions(unittest.TestCase):
    def setUp(self):
        """Set up a test account before each test."""
        self.test_account = {
            "username": "TestUser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "preferences": {
                "cleanliness": Preference.SOMETIMES.value,
                "alcohol": Preference.RARELY.value,
            },
        }
        self.inserted_id = create_account(
            self.test_account["username"],
            self.test_account["email"],
            self.test_account["password"],
            preferences=self.test_account["preferences"],
        )

    def tearDown(self):
        """Clean up the test account after each test."""
        delete_account(self.test_account["username"])

    def test_create_account(self):
        """Test account creation."""
        created_id = create_account(
            "TestCreate",
            "testcreate@example.com",
            "testpassword",
            preferences={
                "cleanliness": Preference.OFTEN.value,
                "alcohol": Preference.NEVER.value,
            },
        )
        self.assertIsNotNone(created_id, "Account creation failed.")
        delete_account("TestCreate")  # Clean up

    def test_update_account(self):
        """Test account update."""
        updates = {
            "prompt": "Updated prompt for testing.",
            "preferences.cleanliness": Preference.OFTEN.value,
        }
        matched, modified = update_account(self.test_account["username"], updates)
        self.assertGreater(matched, 0, "No account matched for updating.")
        self.assertGreater(modified, 0, "No changes were made to the account.")

    def test_delete_account(self):
        """Test account deletion."""
        delete_count = delete_account(self.test_account["username"])
        self.assertGreater(delete_count, 0, "Account deletion failed.")
        # Ensure account is no longer in the database
        remaining = accounts.find_one({"username": self.test_account["username"]})
        self.assertIsNone(remaining, "Account was not fully deleted.")

# Run the tests
if __name__ == "__main__":
    unittest.main()
