import random
import string
from config import get_dynamodb_table, settings
from boto3.dynamodb.conditions import Key
from exceptions import URLAlreadyExistsException, URLNotFoundException
from fastapi import HTTPException
from typing import Optional

urls_table = get_dynamodb_table(settings.URLS_TABLE_NAME)

def generate_short_url(url: str, custom_alias: Optional[str] = None) -> str:
    if custom_alias:
        # Check if custom alias is available
        existing_url = urls_table.get_item(Key={"short_url": custom_alias}).get('Item')
        if existing_url:
            raise HTTPException(status_code=409, detail=f"The alias '{custom_alias}' is already in use.")
        return custom_alias
    else:
        # Automatically retry to generate a new alias if it's already in use
        attempts = 0
        while attempts < 5:
            random_alias = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            existing_url = urls_table.get_item(Key={"short_url": random_alias}).get('Item')
            if not existing_url:
                return random_alias
            attempts += 1
        raise HTTPException(status_code=500, detail="Failed to generate a unique alias after 5 attempts.")

def generate_random_alias(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_alias_taken(alias: str) -> bool:
    response = urls_table.get_item(Key={'short_url': alias})
    return 'Item' in response

def save_url_to_db(short_url: str, original_url: str) -> None:
    url_data = {
        "short_url": short_url,
        "original_url": original_url
    }
    urls_table.put_item(Item=url_data)

def get_original_url(short_url: str) -> str:
    response = urls_table.get_item(Key={'short_url': short_url})
    if 'Item' not in response:
        raise URLNotFoundException(f"URL with alias '{short_url}' not found.")
    return response['Item']['original_url']

def list_all_urls():
    response = urls_table.scan()
    return response.get('Items', [])

