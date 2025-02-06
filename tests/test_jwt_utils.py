import sys
import os
# Add the 'src' directory to sys.path so Python can find jwt_utils.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/utils")))

import unittest
from jwt_utils import generate_jwt, validate_jwt, SECRET_KEY
import jwt
import time
import copy

class TestJWTFunctions(unittest.TestCase):
    def setUp(self):
        """Prepare test data before each test."""
        self.test_payload = {
            "user_id": 123,
            "username": "testuser"
        }

    def test_generate_jwt(self):
        """Test JWT generation."""
        token = generate_jwt(self.test_payload, expires_in=3600)
        
        # Verify token is a string
        self.assertIsInstance(token, str)
        
        # Verify token can be decoded
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(decoded['user_id'], 123)
        self.assertEqual(decoded['username'], 'testuser')
        
        # Verify expiration is set
        self.assertIn('exp', decoded)

    def test_jwt_expiration(self):
        """Test token expiration."""
        token = generate_jwt(self.test_payload, expires_in=1)  # 1 second expiration
        
        # Wait for token to expire
        time.sleep(2)
        
        # Validate should return None for expired token
        decoded = validate_jwt(token)
        self.assertIsNone(decoded)

    def test_invalid_jwt(self):
        """Test invalid token scenarios."""
        # Generate a valid token
        valid_token = generate_jwt(self.test_payload)
        
        # Modify the token to make it invalid
        tampered_token = valid_token + "extra_chars"
        
        # Validate should return None for tampered token
        decoded = validate_jwt(tampered_token)
        self.assertIsNone(decoded)

    def test_jwt_with_different_payload(self):
        """Test JWT with various payload types."""
        test_cases = [
            {"email": "test@example.com"},
            {"roles": ["admin", "user"]},
            {"is_active": True},
            {"score": 95.5}
        ]
        
        for payload in test_cases:
            # Create a copy of the payload to avoid modifying the original
            payload_copy = copy.deepcopy(payload)
            
            token = generate_jwt(payload_copy)
            decoded = validate_jwt(token)
            
            # Verify each payload type can be encoded and decoded correctly
            self.assertIsNotNone(decoded)
            
            # Remove the exp key for comparison
            decoded.pop('exp', None)
            payload_copy.pop('exp', None)
            
            for key, value in payload_copy.items():
                self.assertEqual(decoded[key], value)

# Run the tests
if __name__ == "__main__":
    unittest.main()