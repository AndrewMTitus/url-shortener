import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel, Field
from typing import Optional

dynamodb = boto3.resource('dynamodb')

users_table = dynamodb.Table('UsersTable')
urls_table = dynamodb.Table('URLsTable')

class Token(BaseModel):
    access_token: str
    token_type: str

class URLCreate(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    
class URLRequest(BaseModel):
    url: str
    custom_alias: Optional[str] = None

class User(BaseModel):
    username: str
    hashed_password: str
    url_limit: int = 20
    is_admin: bool = False

    @staticmethod
    def get_user(username: str):
        try:
            response = users_table.get_item(Key={'username': username})
            return response.get('Item')
        except Exception as e:
            print(f"Error fetching user {username}: {e}")
            return None
        
    @staticmethod
    def save_user(user: dict):
        try:
            users_table.put_item(Item=user)
        except Exception as e:
            print(f"Error saving user {user['username']}: {e}")

class URL(BaseModel):
    short_url: str
    original_url: str
    username: str

    @staticmethod
    def save_url(url_data: dict):
        urls_table.put_item(Item=url_data)

    @staticmethod
    def get_url(short_url: str):
        response = urls_table.get_item(Key={'short_url': short_url})
        return response.get('Item')

    @staticmethod
    def get_user_urls(username: str):
        response = urls_table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        return response.get('Items')
