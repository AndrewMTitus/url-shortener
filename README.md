# url-shortener
URL Shortener CLI
A URL Shortener tool that allows users to shorten URLs, retrieve original URLs, and manage shortened URLs through a Command Line Interface (CLI). This project also includes admin functionality for listing all stored URLs.

Features
Shorten a URL.
Create custom short URLs.
Retrieve the original URL from a shortened link.
Admin functionality to list all shortened URLs.
Authentication via JWT tokens.
Table of Contents
1.Installation
2.Configuration
3.Usage
 -Login
 -Shorten URL
 -List URLs (Admin)
 -Lookup URL
4.Testing

1.Installation
 -Clone this repository:

   git clone https://github.com/your-username/url-shortener-cli.git
   cd url-shortener-cli
   
 -Install the necessary dependencies:

   pip install -r requirements.txt
   
 -Ensure you have Python 3.x installed. You can verify this by running:

   python3 --version
   
 -Set up your DynamoDB tables for UsersTable and URLsTable on AWS if you haven't done so already.

2.Configuration
 -Ensure that the configuration is set up correctly in the config.py file. Here's a sample configuration:


    class Settings(BaseSettings):
        SECRET_KEY: str = "your-secret-key"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        USERS_TABLE_NAME: str = "UsersTable"
        URLS_TABLE_NAME: str = "URLsTable"

    settings = Settings()
 -Make sure the AWS DynamoDB table names are correct and that AWS credentials are properly configured on your machine (usually via 
  ~/.aws/credentials).

3.Usage
 -Login
  To start using the CLI, you need to log in first to get a token.

  Run:

  python3 cli.py login
  
  You will be prompted to enter your username and password.

  If the login is successful, your token will be saved locally in token.txt for further use.

 -Shorten URL
 
  To shorten a URL, use the following command:


   python3 cli.py shorten --url "https://example.com"
   
   You can also provide a custom short alias if desired:


   python3 cli.py shorten --url "https://example.com" --custom "exampleAlias"
   
 -List URLs (Admin)
  Admins can list all shortened URLs by using:

   python3 cli.py list-urls
   
  This command will display all stored short URLs along with their original counterparts.

 -Lookup URL
  To retrieve the original URL from a shortened one, use:

   python3 cli.py lookup --short "<short_url>"
   Replace <short_url> with the actual shortened URL.

4.Testing
 -To ensure that the functionality is working as expected, you can run the following test commands:

 Login Test:

  Log in as a user or admin, ensuring that tokens are generated and saved.
  
 Shorten URL Test:

  Test URL shortening with and without custom aliases.
 
 Admin Test:

  Test the ability of the admin to list all URLs.
 
 Lookup Test:

  Test URL lookups to retrieve the original URLs from shortened URLs.

