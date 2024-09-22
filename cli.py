import click
import requests

# Set the base URL of your API
API_BASE_URL = "http://127.0.0.1:8000"

@click.group()
def cli():
    """URL Shortener CLI."""
    pass
# Authenticate and store token
@click.command()
@click.option('--username', prompt='Username', help='Your username')
@click.option('--password', prompt='Password', hide_input=True, help='Your password')
def login(username, password):
    response = requests.post(f"{API_BASE_URL}/token", data={
        'username': username,
        'password': password
    })

    if response.status_code == 200:
        token = response.json().get('access_token')
        with open("token.txt", "w") as token_file:
            token_file.write(token)
        click.echo(f"Logged in successfully. Token saved.")
    else:
        click.echo(f"Failed to log in: {response.text}")

# Function to shorten a URL
@click.command()
@click.option('--url', prompt='URL to shorten', help='The original URL to be shortened.')
@click.option('--custom', default=None, help='Custom alias for the shortened URL.')
def shorten(url, custom):
    try:
        with open("token.txt", "r") as token_file:
            token = token_file.read().strip()

        headers = {
            'Authorization': f"Bearer {token}"
        }
  
        data = {'url': url}
        if custom:
            data['custom_alias'] = custom

        response = requests.post(f"{API_BASE_URL}/create_url", json=data, headers=headers)
        if response.status_code == 200:
            click.echo(f"Shortened URL: {response.json()['short_url']}")
        else:
            click.echo(f"Error: {response.json()['detail']}")
    except FileNotFoundError:
        click.echo("You are not logged in. Please run `python3 cli.py login` to log in.")

# Function to list all URLs (admin functionality)
@click.command()
@click.option('--token', prompt='Admin token', help='JWT Token for admin authentication.')
def list_urls(token):
    """List all URLs (admin functionality)."""
    try:
        with open("token.txt", "r") as token_file:
            token = token_file.read().strip()

        headers = {'Authorization': f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/list_urls", headers=headers)

        if response.status_code == 200:
            urls = response.json()
            for url in urls:
                click.echo(f"{url['short_url']} -> {url['original_url']}")
        else:
            click.echo(f"Error: {response.json()['detail']}")
    except FileNotFoundError:
        click.echo("You are not logged in. Please run `python3 cli.py login` to log in.")

# Function to lookup a short URL
@click.command()
@click.option('--short', prompt='Shortened URL', help='The shortened URL to look up.')
def lookup(short):
    """Look up the original URL from a shortened URL."""
    try:
        response = requests.get(f"{API_BASE_URL}/lookup/{short}")
        if response.status_code == 200:
            click.echo(f"Original URL: {response.json()['original_url']}")
        else:
            click.echo(f"Error: {response.json()['detail']}")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

cli.add_command(login)
cli.add_command(shorten)
cli.add_command(list_urls)
cli.add_command(lookup)

if __name__ == '__main__':
    cli()
