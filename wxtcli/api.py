"""
wxtcli - api.py
Billy Zoellers

Global API object
"""
import requests
from webexteamssdk import WebexTeamsAPI

api = WebexTeamsAPI()

def api_req(resource, method="get", **kwargs):
    """
    Make an API request to Webex that is not contained
    within the Python SDK
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api.access_token}"
    }

    resp = requests.request(
        url=f"{api.base_url}/{resource}",
        method=method,
        headers=headers,
        **kwargs
    )

    resp.raise_for_status()

    if resp.text:
        return resp.json()
    
    return {}
