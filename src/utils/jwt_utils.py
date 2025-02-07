import jwt
import datetime
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Fetch the JWT secret key from environment variables
SECRET_KEY = os.getenv("JWT_SECRET", "default_secret")  # Use a default only in dev
ALGORITHM = "HS256"

# Generates a JWT with the given payload and expiration time.
def generate_jwt(payload: Dict, expires_in: int = 3600) -> str:
    exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
    payload["exp"] = exp_time
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Validates a JWT and returns the decoded payload if valid.
def validate_jwt(token: str) -> Optional[Dict]:
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
    except jwt.InvalidTokenError:
        print("Invalid token.")
    
    return None

print(SECRET_KEY)