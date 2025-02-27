import jwt
import datetime
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Fetch the JWT secret key from environment variables
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

# Generates a JWT given user data
def generate_jwt(email: str, expires_in: int = 86400) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "email": email,
        # "role": role 
        "iat": now.timestamp(),  # token issue date
        "exp": (now + datetime.timedelta(seconds=expires_in)).timestamp()  # token expiration date
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Validates a JWT and returns the decoded payload if valid.
def validate_jwt(token: str) -> Optional[Dict]:
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