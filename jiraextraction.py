import requests
import logging
from requests.auth import HTTPBasicAuth
import textwrap

# Import OpenAI Environment Variables
from jiravars import (JIRA_BASE_URL, JIRA_RETRIEVE_ENDPOINT, 
                           JIRA_CREATE_ENDPOINT, JIRA_USER_NAME, JIRA_API_TOKEN)

MAX_JIRA_COMMENT_LENGTH = 32767  # JIRA comment character limit

def filter_dict(d, whitelist):
    """
    Recursively filter a dictionary to only include keys in the whitelist.
    """
    result = {}
    for k, v in d.items():
        if k in whitelist:
            if isinstance(v, dict):
                result[k] = filter_dict(v, whitelist[k])
            elif isinstance(v, list) and '__array__' in whitelist[k]:
                result[k] = [filter_dict(elem, whitelist[k]['__array__']) if isinstance(elem, dict) else elem for elem in v]
            else:
                result[k] = v
    return result


# def retrieve_jira_ticket_from_file(jira_ticket):
#     """
#     Read the json file <jira_ticket>.json and return the contents as a sting
#     """
#     with open(f"{jira_ticket}.json") as f:
#         return json.load(f)

    
    
def retrieve_jira_ticket_from_server(jira_ticket, ticket_type, timeout=10):
    """
    Retrieve a JIRA ticket's details from the server using the JIRA REST API.
    """
    url = JIRA_RETRIEVE_ENDPOINT.format(jira_ticket)
    
    # Create a session to handle cookies and SSO
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_USER_NAME, JIRA_API_TOKEN)
    
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        try:
            # Comment out response print for now - C. Finnegan - Jan 24th 2025
            # print(response.text)
            print(f"\nRetrieving JIRA {ticket_type} ticket from server...")
            return response.json()
        except ValueError as e:
            logging.error(f"Error decoding JSON response: {e}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving JIRA {ticket_type} ticket: {e} {response.text}")
        return None



def add_label_to_jira_ticket(jira_ticket, label, timeout=10):
    """
    Add a label to a JIRA ticket using the JIRA REST API.
    """
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{jira_ticket}"
    auth = HTTPBasicAuth(JIRA_USER_NAME, JIRA_API_TOKEN)
    headers = {
        "Content-Type": "application/json"
    }
    
    # Get current labels first to avoid duplicates
    current_ticket = retrieve_jira_ticket_from_server(jira_ticket, "LABEL")
    print("\nStage 2b: Adding Label to JIRA ticket...")
    if current_ticket and 'fields' in current_ticket and 'labels' in current_ticket['fields']:
        current_labels = current_ticket['fields']['labels']
        if label not in current_labels:
            current_labels.append(label)
            payload = {
                "update": {
                    "labels": [{"add": label}]
                }
            }
            
            try:
                response = requests.put(url, auth=auth, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                logging.error(f"Error adding label to JIRA ticket: {e}")
                return False
    
    return True




def create_jira_comment(jira_ticket, comment, timeout=10):
    """
    Create a comment on a JIRA ticket using the JIRA REST API.
    """
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{jira_ticket}/comment"
    auth = HTTPBasicAuth(JIRA_USER_NAME, JIRA_API_TOKEN)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "body": comment
    }
    
    try:
        response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating JIRA comment: {e} {response.text}")
        return None
    
    try:
        response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating JIRA comment: {e} {response.text}")
        return None



def chunk_text(text, chunk_size=MAX_JIRA_COMMENT_LENGTH):
    """
    Chunk text into smaller pieces to fit within JIRA's comment character limit.
    """
    return textwrap.wrap(text, chunk_size, replace_whitespace=False)

def create_jira_comments_in_chunks(jira_ticket, comment, timeout=10):
    """
    Create comments on a JIRA ticket in chunks to fit within JIRA's comment character limit.
    """
    print("\nStage 2c: Adding Bdd comments to JIRA ticket...")
    chunks = chunk_text(comment)
    for chunk in chunks:
        create_jira_comment(jira_ticket, chunk, timeout)



