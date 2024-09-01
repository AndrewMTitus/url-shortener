from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    hashed_password: str
    url_limit: int = 20
    is_admin: bool = False

    @staticmethod
    def get_user(username: str):
        # Logic to retrieve user from DynamoDB
        pass

    @staticmethod
    def save_user(user: dict):
        # Logic to save user to DynamoDB
        pass

class URL(BaseModel):
    short_url: str
    original_url: str
    username: str

    @staticmethod
    def save_url(url_data: dict):
        # Logic to save URL to DynamoDB
        pass

    @staticmethod
    def get_url(short_url: str):
        # Logic to retrieve URL from DynamoDB
        pass

    @staticmethod
    def get_user_urls(username: str):
        # Logic to retrieve URLs by user from DynamoDB
        pass

class URLRequest(BaseModel):
    url: str
    custom_alias: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
