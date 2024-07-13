import unittest
from fastapi.testclient import TestClient
from main import app
import boto3
from botocore.exceptions import ClientError

client = TestClient(app)

#DynamoDB table name
TABLE_NAME = "url_shortener"

class TestURLShortener(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #Setup DynamoDB client and table references
        cls.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        cls.table = cls.dynamodb.Table(TABLE_NAME)
    
    def setUp(self):
        #Clear the table before each test
        self.clear_table()

    def tearDown(self):
        #Clear the table after each set
        self.clear_table()
    
    def clear_table(self):
        #Scan and delete all items from the table
        scan = self.table.scan()
        with self.table.batch_writer() as batch:
            for each in scan['Items']:
                batch.delete_item(Key={'short_url': each['short_url']})

    def test_shorten_url(self):
        response = client.post("/shorten_url", json={"url": 
"https://www.example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())

    def test_shorten_url_with_custom_alias(self):
        response = client.post("/shorten_url", json={"url": 
"https://www.example.com", "custom_alias": "custom123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["short_url"], 
"http://localhost:8000/custom123")

    def test_shorten_url_duplicate_custom_alias(self):
        client.post("/shorten_url", json={"url": 
"https://www.example.com", "custom_alias": "custom123"})
        response = client.post("/shorten_url", json={"url": 
"https://www.example.com/other", "custom_alias": "custom123"})
        self.assertEqual(response.status_code, 409)

    def test_list_urls(self):
        client.post("shorten_url", json={"url": 
"https://www.example.com"})
        response = client.get("/list_urls")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_redirect_url(self):
        client.post("/shorten_url", json={"url": 
"https://www.example.com", "custom_alias": "example"})
        response = client.get("/example")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["original_url"], 
"https://www.example.com")

    def test_redirect_url_not_found(self):
        response = client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
