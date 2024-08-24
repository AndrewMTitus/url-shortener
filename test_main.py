import unittest
from fastapi.testclient import TestClient
from main import app
import boto3
from botocore.exceptions import ClientError
from config import get_dynamodb_table, settings

client = TestClient(app)

#DynamoDB table name
TABLE_NAME = "url_shortener"
urls_table = get_dynamodb_table(settings.URLS_TABLE_NAME)

def setup_function():
    urls_table.put_item(Item={'short_url': 'test1', 'original_url': 'https://example.com'})
    urls_table.put_item(Item={'short_url': 'test2', 'original_url': 'https://example.org'})

def teardown_function():
    urls_table.delete_item(Key={'short_url': 'test1'})
    urls_table.delete_item(Key={'short_url': 'test2'})

def test_shorten_url():
    response = client.post("/shorten_url", json={"url": "https://example.com"})
    assert response.status_code == 200
    assert "short_url" in response.json()

def test_redirect_url():
    response = client.get("/test1")
    assert response.status_code == 200
    assert response.json() == {"original_url": "https://example.com"}

def test_list_urls():
    response = client.get("/list_urls")
    assert response.status_code == 200
    assert len(response.json()) >= 2  # Adjust based on your database content

def test_shorten_url_conflict():
    response = client.post("/shorten_url", json={"url": "https://example.com", "custom_alias": "test1"})
    assert response.status_code == 409

def test_url_not_found():
    response = client.get("/nonexistent")
    assert response.status_code == 404
