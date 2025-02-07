import sys
import os
import unittest
import jwt
import time

# Add the 'src' directory to sys.path so Python can find jwt_utils.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/utils")))

from jwt_utils import generate_jwt, validate_jwt, SECRET_KEY

class TestJWTFunctions(unittest.TestCase):
    def setUp(self):
        """Prepare test data before each test."""
        self.test_email = "testuser@example.com"

    def test_generate_jwt(self):
        """Test JWT generation."""
        token = generate_jwt(self.test_email, expires_in=3600)
        
        # Verify token is a string
        self.assertIsInstance(token, str)
        
        # Verify token can be decoded
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(decoded['email'], self.test_email)
        
        # Verify expiration is set
        self.assertIn('exp', decoded)

    def test_jwt_expiration(self):
        """Test token expiration."""
        token = generate_jwt(self.test_email, expires_in=1)  # 1 second expiration
        
        # Wait for token to expire
        time.sleep(2)
        
        # Validate should return None for expired token
        decoded = validate_jwt(token)
        self.assertIsNone(decoded)

    def test_invalid_jwt(self):
        """Test invalid token scenarios."""
        # Generate a valid token
        valid_token = generate_jwt(self.test_email)
        
        # Modify the token to make it invalid
        tampered_token = valid_token + "extra_chars"
        
        # Validate should return None for tampered token
        decoded = validate_jwt(tampered_token)
        self.assertIsNone(decoded)

    def test_jwt_with_different_emails(self):
        """Test JWT with various email addresses."""
        emails = ["user1@example.com", "admin@example.com", "guest@example.com"]
        
        for email in emails:
            token = generate_jwt(email)
            decoded = validate_jwt(token)
            
            self.assertIsNotNone(decoded)
            self.assertEqual(decoded['email'], email)

# Run the tests
if __name__ == "__main__":
    unittest.main()
