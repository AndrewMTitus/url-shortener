import os
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
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
        username = payload.get("sub")
        if username is None:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Could not validate credentials"}, headers={"WWW-Authenticate": "Bearer"})
        return username
    except JWTError:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Could not validate credentials"}, headers={"WWW-Authenticate": "Bearer"})

def authenticate_user(username: str, password: str):
    try:
        response = users_table.get_item(Key={"username": username})
        user = response.get("Item")
        if not user:
            logging.error("User not found")
            return False
        if not verify_password(password, user["hashed_password"]):
            logging.error("Password verification failed")
            return False
        return User(**user)
    except ClientError as e:
        logging.error(f"Error accessing DynamoDB: {e}")
        return False
    except BotoCoreError as e:
        logging.error(f"Error with the AWS SDK: {e}")
        return False

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials"
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = jwt.decode(jwtoken, SECRET_KEY, algorithms=[ALGORITHM])
            isTokenValid = True
        except:
            payload = None
        return isTokenValid


