import boto3
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "4163979aafcfbef09c4feeba2a9e826ec0dc7ac52f4d819c54c3a2a478957dcb"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AWS_REGION: str = "us-east-1"
    USERS_TABLE_NAME: str = "UsersTable"
    URLS_TABLE_NAME: str = "URLsTable"

   

    class Config:
        env_file = ".env"

settings = Settings()

def get_dynamodb_resource():
    return boto3.resource('dynamodb', region_name='us-east-1')


def get_dynamodb_table(table_name: str):
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)

