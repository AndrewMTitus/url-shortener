import hashlib
from botocore.exceptions import ClientError
from config import get_dynamodb_table
from exceptions import URLAlreadyExistsException, URLNotFoundException
from validation import is_valid_url

table = get_dynamodb_table('url_shortener')

def generate_short_url(url: str, custom_alias: str = None) -> str:
    """
    Generate a short URL. If a custom alias is provided, use it; 
otherwise, generate a hash.

    Parameters:
    url (str): The original URL to be shortened.
    custom_alias (str): An optional custom alias for the short URL.

    Returns:
    str: The generated short URL.

    Raises:
    ValueError: If the URL is invalid or if the custom alias is not 
alphanumeric.
    URLAlreadyExistsException: If the generated short URL already exists.
    ClientError: If there is an error with DynamoDB.
    """
    if not is_valid_url(url):
        raise ValueError("Invalid URL")

    if custom_alias and not custom_alias.isalnum():
        raise ValueError("Custom alias must be alphanumeric")

    if custom_alias:
        short_url = custom_alias
    else:
        short_url = hashlib.sha256(url.encode()).hexdigest()[:8]

    try:
        response = table.get_item(Key={'short_url': short_url})
        if 'Item' in response:
            raise URLAlreadyExistsException("Short URL already exists.")
    except ClientError as e:
        print(e.response['Error']['Message'])
    
    try:
        table.put_item(Item={'short_url': short_url, 'original_url': url})
    except ClientError as e:
        print(e.response['Error']['Message'])
    
    return short_url

def get_original_url(short_url: str) -> str:
    """
    Retrieve the original URL given a short URL.

    Parameters:
    short_url (str): The short URL to look up.

    Returns:
    str: The original URL.

    Raises:
    URLNotFoundException: If the short URL does not exist.
    ClientError: If there is an error with DynamoDB.
    """
    try:
        response = table.get_item(Key={'short_url': short_url})
        if 'Item' in response:
            return response['Item']['original_url']
        else:
            raise URLNotFoundException("Short URL does not exist")
    except ClientError as e:
        print(e.response['Error']['Message'])

def list_all_urls() -> list:
    """
    List all short URLs and their corresponding original URLs.

    Returns:
    list: A list of dictionaries containing short URLs and their original 
URLs.

    Raises:
    ClientError: If there is an error with DynamoDB.
    """
    try:
        response = table.scan()
        return response['Items']
    except ClientError as e:
        print(e.response['Error']['Message'])

