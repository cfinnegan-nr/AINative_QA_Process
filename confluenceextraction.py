import configparser
import requests
from requests.auth import HTTPBasicAuth
import json
import os
from bs4 import BeautifulSoup


# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve Confluence configuration
# confluence_url = config['confluence']['url']
# username = config['confluence']['username']
# api_token = config['confluence']['api_token']

# Retrieve Confluence configuration from environment variables
confluence_url = os.getenv("CONFLUENCE_URL")  # Get the Confluence URL
if not confluence_url:
    raise ValueError("CONFLUENCE_URL environment variable not set")

username = os.getenv("JIRA_USER_NAME")
if not username:
    raise ValueError("JIRA_USER_NAME environment variable not set")

api_token = os.getenv("JIRA_API_TOKEN")
if not api_token:
    raise ValueError("JIRA_API_TOKEN environment variable not set")



def get_page_content(page_id):
    print("\nRetrieving Confluence data from server...")
    
    url = f"{confluence_url}/content/{page_id}?expand=body.storage"
    auth = HTTPBasicAuth(username, api_token)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        content = response.json()
        html_content = content['body']['storage']['value']
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Clean up extra whitespace
        clean_text = '\n'.join(line.strip() for line in text_content.splitlines() if line.strip())
        
        return clean_text
    else:
        print(f"Failed to retrieve page content. Status code: {response.status_code}")
        return None


if __name__ == "__main__":
    page_id = config.get('confluence', 'page_id')
    print(get_page_content(page_id))