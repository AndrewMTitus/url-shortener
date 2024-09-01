import boto3
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    USERS_TABLE_NAME: str = "UsersTable"
    URLS_TABLE_NAME: str = "URLsTable"

settings = Settings()

def get_dynamodb_resource():
    return boto3.resource('dynamodb', region_name='us-east-1')

def get_dynamodb_table(table_name: str):
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)
