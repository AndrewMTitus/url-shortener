from config import get_dynamodb_table, settings
from auth import get_password_hash, verify_password
from models import UserCreate, URLRequest
from exceptions import URLLimitReachedException

users_table = get_dynamodb_table(settings.USERS_TABLE_NAME)
urls_table = get_dynamodb_table(settings.URLS_TABLE_NAME)

def create_user_in_db(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "hashed_password": hashed_password,
        "url_limit": 20,
        "is_admin": False
    }
    users_table.put_item(Item=user_data)
    return {"message": f"User '{user.username}' created successfully."}

def list_urls():
    response = urls_table.scan()
    return response.get('Items', [])

def list_my_urls(current_user):
    response = urls_table.query(
        IndexName="username-index",
        KeyConditionExpression="username = :username",
        ExpressionAttributeValues={":username": current_user.username},
    )
    return response.get('Items', [])

def change_password(current_user, new_password: str):
    hashed_password = get_password_hash(new_password)
    users_table.update_item(
        Key={"username": current_user.username},
        UpdateExpression="SET hashed_password = :hashed_password",
        ExpressionAttributeValues={":hashed_password": hashed_password},
    )
    return {"message": "Password changed successfully."}

def create_url(current_user, url_request: URLRequest):
    short_url = generate_short_url(url_request.url, url_request.custom_alias)
    url_data = {
        "short_url": short_url,
        "original_url": url_request.url,
        "username": current_user.username
    }
    urls_table.put_item(Item=url_data)
    return {"short_url": short_url}

def update_url_limit(username: str, new_limit: int):
    user = users_table.get_item(Key={"username": username}).get('Item')
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    current_url_count = urls_table.query(
        IndexName="username-index",
        KeyConditionExpression="username = :username",
        ExpressionAttributeValues={":username": username},
    ).get('Count', 0)
    
    if new_limit < current_url_count:
        raise HTTPException(status_code=400, detail="New limit is less than current number of URLs.")
    
    users_table.update_item(
        Key={"username": username},
        UpdateExpression="SET url_limit = :new_limit",
        ExpressionAttributeValues={":new_limit": new_limit},
    )
    return {"message": f"Limit updated successfully for '{username}'."}
