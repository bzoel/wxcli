"""
wxtcli - workspace.py
David Rice

Workspace module
"""
from select import select
import typer
from enum import Enum
from typing import Optional
from wxtcli.console import console
from wxtcli.api import api, api_req
from wxtcli.helpers.formatting import table_with_columns, humanize_wxt_datetime
from rich.progress import track

app = typer.Typer()

@app.command()
def list_workspace_callerid(
    location_name: str = typer.Option(None, help="Webex Calling Location Name"),
    org_id: str = typer.Option(None, help="Organization ID")):
    """
    List Workspace CallerID settings for all workspaces (in an org, if specified)
    """

    orgId=None
    if (org_id is not None):
        orgId = api_req(f"organizations/{org_id}")["id"]
    
    numbers = []
    if (orgId is not None):
        numbers = api_req("telephony/config/numbers", params = {
            "orgId": orgId,
            "ownerType": "PLACE",
        })
    else:
        numbers = api_req("telephony/config/numbers", params = {
            "ownerType": "PLACE",
        })


    table = table_with_columns(
        ["Workspace","Extension", "DID", "CallerID-Number", "CallerID-Name"], title="Workspace Info"
    )

    for number in numbers:
        workspaceId = number["owner"]["id"]
        workspaceFirstName = number["owner"]["firstName"]
        callerIdNumber = ""
        callerIdName = ""

        if (orgId is not None):
            callerIdInfo = api_req(f"workspaces/{workspaceId}/features/callerId", params = {
            "orgId": orgId,
            })
        else:
            callerIdInfo = api_req(f"workspaces/{workspaceId}/features/callerId")
            
        match callerIdInfo["selected"]:
            case "DIRECT_LINE":
                callerIdNumber = callerIdInfo["directNumber"]
            case "LOCATION_NUMBER":
                callerIdNumber = callerIdInfo["locationNumber"]
            case "CUSTOM":
                callerIdNumber = callerIdInfo["customNumber"]

        match callerIdInfo["externalCallerIdNamePolicy"]:
            case "DIRECT_LINE":
                callerIdName = callerIdInfo["displayName"]
            case "LOCATION_NUMBER":
                callerIdName = callerIdInfo["locationExternalCallerIdName"]
            case "OTHER":
                callerIdName = callerIdInfo["customExternalCallerIdName"]
            


        table.add_row(
            workspaceFirstName,
            number["extension"] if "extension" in number.keys() else "N/A",
            number["phoneNumber"] if "phoneNumber" in number.keys() else "N/A",
            callerIdNumber,
            callerIdName,
        )

    console.print(table)

