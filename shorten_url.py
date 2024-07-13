import boto3
from botocore.exceptions import ClientError
import hashlib

#Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('url_shortener')

def generate_short_url(url: str, custom_alias: str = None) -> str:
    """
    Generate a short URL. If a custom alias is provided, use it; 
otherwise, generate a hash.
    """
    if custom_alias:
        short_url = custom_alias
    else:
        short_url = hashlib.sha256(url.encode()).hexdigest()[:8]
    
    #Check for collisions in the database
    try:
        response = table.get_item(Key={'short_url': short_url})
        if 'Item' in response:
            raise ValueError("Short URL already exists.")
    except ClientError as e:
        print(e.response['Error']['Message'])
    
    #Store the URL mapping in the database
    try:
        table.put_item(Item={'short_url': short_url, 'original_url': url})
    except ClientError as e:
        print(e.response['Error']['Message'])
    return short_url

def get_original_url(short_url: str) -> str:
    """
    Retrieve the original URL given a short URL.
    """
    try:
        response = table.get_item(Key={'short_url': short_url})
        if 'Item' in response:
            return response['Item']['original_url']
        else:
            raise ValueError("Short URL does not exist")
    except ClientError as e:
        print(e.response['Error']['Message'])

def list_all_urls() -> list:
    """
    List all short URLs and their corresponding original URLs.
    """
    try:
        response = table.scan()
        return response['Items']
    except ClientError as e:
        print(e.response['Error']['Message'])

