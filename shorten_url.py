import random
import string
from config import get_dynamodb_table, settings
from boto3.dynamodb.conditions import Key
from exceptions import URLAlreadyExistsException, URLNotFoundException

urls_table = get_dynamodb_table(settings.URLS_TABLE_NAME)

def generate_short_url(original_url: str, custom_alias: str = None) -> str:
    if custom_alias:
        if is_alias_taken(custom_alias):
            raise URLAlreadyExistsException(f"The alias '{custom_alias}' is already in use.")
        short_url = custom_alias
    else:
        short_url = generate_random_alias()
        while is_alias_taken(short_url):
            short_url = generate_random_alias()

    save_url_to_db(short_url, original_url)
    return short_url

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

