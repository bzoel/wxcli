"""
wxtcli - calling.py
Billy Zoellers / David Rice

Calling module
"""
from select import select
import typer
from enum import Enum
from typing import Optional
from wxcli.console import console
from wxcli.api import api, api_req
from wxcli.helpers.formatting import table_with_columns, humanize_wxt_datetime
from rich.progress import track

app = typer.Typer()

class CallerIdNamePolicy(str, Enum):
    """
    Name policy for Caller ID
    """
    DIRECT_LINE = "DIRECT_LINE"
    LOCATION = "LOCATION"
    OTHER = "OTHER"

class CallerIdSelectedType(str, Enum):
    """
    Numer type for Caller ID
    """
    DIRECT_LINE = "DIRECT_LINE"
    LOCATION_NUMER = "LOCATION_NUMBER"
    CUSTOM = "CUSTOM"

@app.command()
def update_user_cid(
    user_email: str = typer.Argument(..., help="Webex user email"),
    selected_type: Optional[CallerIdSelectedType] = typer.Option(None, help="Type of number"),
    name_policy: Optional[CallerIdNamePolicy] = typer.Option(None, help="Caller ID name policy"),
    custom_number: Optional[str] = typer.Option(None, help="Custom number"),
    cid_first_name: Optional[str] = typer.Option(None, help="CID first name"),
    cid_last_name: Optional[str] = typer.Option(None, help="CID last name"),
    other_name: Optional[str] = typer.Option(None, help="Other CID name")
):
    """
    Update the Caller ID for a Webex Calling user
    """
    # Require a custom number when CUSTOM type is selected
    if selected_type == CallerIdSelectedType.CUSTOM and custom_number is None:
        console.print(f"[red]You must specify a '--custom-number'")
        raise typer.Abort()

    # Require a custom name when OTHER name is selected
    if name_policy == CallerIdNamePolicy.OTHER and other_name is None:
        console.print(f"[red]You must specify a '--other-name'")
        raise typer.Abort()

    # API requires both values to be set at same time
    if name_policy is not None and selected_type is None:
        console.print(f"[red]You must set '--selected-type' at the same time as '--name-policy'")

    # Find Webex Calling person
    person = api_req("people", params={
        "email": user_email,
        "callingData": True,
    })
    if not person:
        console.print(f"[red]Person with email '{user_email}' not found.")
        raise typer.Abort()
    person = person[0]
    console.print(f"[green]Found user [bold]{person['displayName']}[/bold] with extension [bold]{person['extension']}[/bold]")

    # Get current CID data
    cid_data = api_req(f"people/{person['id']}/features/callerId")
    console.print(f" [green]Current CID Type: {cid_data['selected']}")

    # Update values
    updated_values = {}

    # Update CID type
    if selected_type is not None:
        updated_values["selected"] = selected_type.value
        if selected_type == CallerIdSelectedType.CUSTOM:
            updated_values["customNumber"] = custom_number

    # Update CID name
    if name_policy is not None:
        updated_values["externalCallerIdNamePolicy"] = name_policy.value
        if name_policy == CallerIdNamePolicy.OTHER:
            updated_values["customExternalCallerIdName"] = other_name

    # Update CID first name
    if cid_first_name is not None:
        updated_values["firstName"] = cid_first_name

    # Update CID last name
    if cid_last_name is not None:
        updated_values["lastName"] = cid_last_name

    # Commit updated values
    console.print("[yellow]The following values will be updated:")
    console.print(updated_values)
    api_req(f"people/{person['id']}/features/callerId", method="put", json=updated_values)


{
    "selected": "CUSTOM",
    "customNumber": "8594257735"
}

@app.command()
def list_caller_ids(
    location_name: str = typer.Argument(..., help="Webex Calling Location Name"),
    org_id: str = typer.Option(None, help="Organization ID")
):
    """
    List caller IDs for all people in a location
    """
    orgId=None
    if (org_id is not None):
        orgId = api_req(f"organizations/{org_id}")["id"]

    # First locationId of interest
    if (org_id is not None):
        locations = api_req("locations", params ={
        "orgId": org_id,
    })
    else:  
        locations = api_req("locations")
    locationId = next(location["id"] for location in locations if location["name"] == location_name)

    # Find people belonging to that locationId
    if (org_id is not None):
        people = api_req("people", params={
            "callingData": True,
            "locationId": locationId,
            "orgId": orgId,
        })
    else:
        people = api_req("people", params={
            "callingData": True,
            "locationId": locationId,
        })

    # Find callerId for each person
    table = table_with_columns(
        ["Person", "Extension", "Caller ID Type", "Caller ID Number"], title="Caller ID Info"
    )
    for person in track(people):
        if (org_id is not None):
            caller_id = api_req(f"people/{person['id']}/features/callerId", params={
            "orgId": orgId,
        })
        else:
            caller_id = api_req(f"people/{person['id']}/features/callerId")

        caller_id_number = "Unknown"
        if caller_id["selected"] == "DIRECT_LINE":
            caller_id_number = caller_id["directNumber"]
        elif caller_id["selected"] == "LOCATION_NUMBER":
            caller_id_number = caller_id["locationNumber"]
        elif caller_id["selected"] == "CUSTOM":
            caller_id_number = caller_id["customNumber"]

        table.add_row(
            person["displayName"],
            person["extension"],
            caller_id["selected"],
            caller_id_number
        )
    console.print(table)


@app.command()
def update_location_allcids(
    location_name: str = typer.Argument(..., help="Webex Calling Location Name"),
    caller_id: str = typer.Argument("LOCATION_NUMBER", help="Caller ID | LOCATION_NUMBER | DIRECT_LINE"),
    org_id: str = typer.Option(None, help="Organization ID")
):
    """
    Update caller IDs for all people in a location
    """

    orgId=None
    if (org_id is not None):
        orgId = api_req(f"organizations/{org_id}")["id"]
    
    # Determine Caller ID  type
    caller_id_types = ["LOCATION_NUMBER", "DIRECT_LINE"]
    custom_number = None
    if(caller_id not in caller_id_types):
        custom_number = caller_id
        caller_id = "CUSTOM"

    # First locationId of interest
    if (org_id is not None):
        locations = api_req("locations", params ={
        "orgId": org_id,
    })
    else:  
        locations = api_req("locations")
    locationId = next(location["id"] for location in locations if location["name"] == location_name)

    # Find people belonging to that locationId
    if (org_id is not None):
        people = api_req("people", params={
        "callingData": True,
        "locationId": locationId,
        "orgId": orgId,
    })
    else:
        people = api_req("people", params={
            "callingData": True,
            "locationId": locationId,
        })

    # Set callerId for each person

    for person in track(people):
        if (custom_number == None):
            if (org_id is not None):
                caller_id_resp = api_req(f"people/{person['id']}/features/callerId", method = "put", json = {
                    "selected" : caller_id,
                }, params= {
                "orgId": orgId,
                })
            else:
                caller_id_resp = api_req(f"people/{person['id']}/features/callerId", method = "put", json = {
                    "selected" : caller_id,
                })
        else:
            if (org_id is not None):
                caller_id_resp = api_req(f"people/{person['id']}/features/callerId", method = "put", json = {
                    "selected" : caller_id,
                    "customNumber" : custom_number,
                }, params= {
                "orgId": orgId,
                })
            else:
                caller_id_resp = api_req(f"people/{person['id']}/features/callerId", method = "put", json = {
                    "selected" : caller_id,
                    "customNumber" : custom_number
                })


@app.command()
def all_phone_apply_config(
    location_name: str = typer.Argument(..., help="Webex Calling Location Name"),
    org_id: str = typer.Option(None, help="Organization ID")
):
    """
    List caller IDs for all people in a location
    """
    orgId=None
    if (org_id is not None):
        orgId = api_req(f"organizations/{org_id}")["id"]

    # First locationId of interest
    if (org_id is not None):
        locations = api_req("locations", params ={
        "orgId": org_id,
    })
    else:  
        locations = api_req("locations")
    locationId = next(location["id"] for location in locations if location["name"] == location_name)

    # Find people belonging to that locationId
    if (org_id is not None):
        people = api_req("people", params={
            "callingData": True,
            "locationId": locationId,
            "orgId": orgId,
        })
    else:
        people = api_req("people", params={
            "callingData": True,
            "locationId": locationId,
        })

    # Find callerId for each person
    table = table_with_columns(
        ["Person", "Extension", "Phone Model", "MAC Address", "Type"], title="User Phone Info"
    )
    for person in track(people):
        if (org_id is not None):
            devices = api_req(f"telephony/config/people/{person['id']}/devices", params={
            "orgId": orgId,
        })
        else:
            devices = api_req(f"telephony/config/people/{person['id']}/devices")
        
        #console.print(devices["devices"])
        for device in devices["devices"]:
            device_type=device["model"]
            device_mac=device["mac"]
            table.add_row(
                person["displayName"],
                person["extension"],
                device["model"],
                device["mac"],
                device["type"]
            )
            if (device["type"] == "SHARED_CALL_APPEARANCE"):
                console.print(device['id'])
            #if (device["type"] == "PRIMARY"):
            #    if (org_id is not None):
            #        result = api_req(f"telephony/config/devices/{device['id']}/actions/applyChanges/invoke", method="post", params={
            #            "orgId": orgId,
            #        })
            #    else:
            #        result = api_req(f"telephony/config/devices/{device['id']}/actions/applyChanges/invoke", method="post")
            
            #result = api_req(f"telephony/config/devices/{device['id']}/settings")
            #console.print(result)
    #console.print(table)            

    
