import os

# Load JIRA environment variables
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL', 'https://netreveal.atlassian.net')
JIRA_RETRIEVE_ENDPOINT = os.getenv('JIRA_RETRIEVE_ENDPOINT', 'https://netreveal.atlassian.net/rest/api/2/issue/{}?fields=description%2Ccomment%2Csummary%2Clabels')
JIRA_CREATE_ENDPOINT = os.getenv('JIRA_CREATE_ENDPOINT', 'https://netreveal.atlassian.net/rest/api/2/issue')
JIRA_USER_NAME = os.getenv('JIRA_USER_NAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

