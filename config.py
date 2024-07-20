import boto3

def get_dynamodb_resource():
    return boto3.resource('dynamodb')

def get_dynamodb_table(table_name: str):
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)

