import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration from environment variables
token_secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
token_algorithm = os.getenv("ALGORITHM", "HS256")
token_expiry_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    :param password: Plain text password
    :return: Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    :param plain_password: Plain text password
    :param hashed_password: Hashed password to compare against
    :return: Boolean indicating if password is correct
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    
    :param data: Payload data to encode in the token
    :param expires_delta: Optional custom expiration time
    :return: Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=token_expiry_minutes)
    
    to_encode.update({"exp": expire})
    
    # Encode the token
    encoded_jwt = jwt.encode(to_encode, token_secret_key, algorithm=token_algorithm)
    return encoded_jwt

def decode_token(token: str):
    """
    Decode and validate a JWT token.
    
    :param token: JWT token to decode
    :return: Decoded token payload
    :raises: HTTPException if token is invalid
    """
    try:
        payload = jwt.decode(token, token_secret_key, algorithms=[token_algorithm])
        return payload
    except JWTError:
        return None