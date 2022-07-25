"""
wxtcli - api.py
Billy Zoellers

Global API object
"""
import requests
from webexteamssdk import WebexTeamsAPI
from wxtcli.console import console

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

    # Handle pagination
    if "next" in resp.links.keys():
        next_resource = resp.links["next"]["url"].replace("https://webexapis.com/v1/", "")
        console.log(next_resource)
        return resp.json()["items"] + api_req(next_resource)

    if resp.text:
        if "items" in resp.json().keys():
            return resp.json()["items"]
        return resp.json()
    
    return {}
