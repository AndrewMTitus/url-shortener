import os
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends, Request
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings, get_dynamodb_table
from models import User
from jose import jwt, JWTError
from botocore.exceptions import ClientError, BotoCoreError
from fastapi.responses import JSONResponse

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables for configuration
SECRET_KEY = os.getenv('SECRET_KEY', settings.SECRET_KEY)
ALGORITHM = os.getenv('ALGORITHM', settings.ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get DynamoDB table from settings
users_table = get_dynamodb_table(settings.USERS_TABLE_NAME)

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decode_access_token(jwtoken)
        except:
            payload = None
        return bool(payload)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logging.info("Access token created successfully.")
        return encoded_jwt
    except Exception as e:
        logging.error(f"Failed to create access token: {e}")
        raise

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Function to authenticate a user (verify username and password)
def authenticate_user(username: str, password: str) -> User:
    response = users_table.get_item(Key={"username": username})
    user = response.get("Item")
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return User(**user)

# Function to get the current user based on the JWT token
def get_current_user(token: str = Depends(JWTBearer())) -> User:
    try:
        # Decode the JWT token
        payload = decode_access_token(token)
        username: str = payload.get("sub")  # Extract the username from the token

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Query DynamoDB to get the user by username
        response = users_table.get_item(Key={"username": username})
        user = response.get("Item")

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return User(**user)  # Return the User object
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")



