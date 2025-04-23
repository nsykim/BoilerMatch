import jwt
import datetime
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Fetch the JWT secret key from environment variables
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def generate_jwt(email: str, expires_in: int = 86400) -> str:
    """
    Generate a JWT token with the given email and expiration time.
    
    Args:
        email (str): The email to include in the token.
        expires_in (int): The expiration time in seconds. Default is 86400 seconds (1 day).
    
    Returns:
        str: The generated JWT token.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "email": email,
        "iat": now.timestamp(),  # token issue date
        "exp": (now + datetime.timedelta(seconds=expires_in)).timestamp()  # token expiration date
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def validate_jwt(token: str) -> Optional[Dict]:
    """
    Validate the JWT token and return the payload if valid.
    
    Args:
        token (str): The JWT token to validate.
        
    Returns:
        Optional[Dict]: The decoded payload if the token is valid, otherwise None.
    """
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]
    
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return {"email": -1}
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return {"email": -1}