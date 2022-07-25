"""
wxtcli - people.py
Billy Zoellers

People module
"""
import typer
from wxtcli.console import console
from wxtcli.api import api, api_req
from wxtcli.helpers.formatting import table_with_columns, humanize_wxt_datetime
from rich.progress import track

app = typer.Typer()

@app.command()
def list_caller_ids(
    location_name: str = typer.Argument(..., help="Webex Calling Location Name")
):
    """
    List caller IDs for all people in a location
    """
    # First locationId of interest
    locations = api_req("locations")
    locationId = next(location["id"] for location in locations if location["name"] == location_name)

    # Find people belonging to that locationId
    people = api_req("people", params={
        "callingData": True,
        "locationId": locationId,
    })

    # Find callerId for each person
    table = table_with_columns(
        ["Person", "Extension", "Caller ID Type", "Caller ID Number"], title="Caller ID Info"
    )
    for person in track(people):
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
    caller_id: str = typer.Argument("LOCATION_NUMBER", help="Caller ID | LOCATION_NUMBER | DIRECT_LINE")
):
    """
    Update caller IDs for all people in a location
    """
    # Determine Caller ID  type
    caller_id_types = ["LOCATION_NUMBER", "DIRECT_LINE"]
    custom_number = None
    if(caller_id not in caller_id_types):
        custom_number = caller_id
        caller_id = "CUSTOM"

    # First locationId of interest
    locations = api_req("locations")
    locationId = next(location["id"] for location in locations if location["name"] == location_name)

    # Find people belonging to that locationId
    people = api_req("people", params={
        "callingData": True,
        "locationId": locationId,
    })

    # Set callerId for each person

    for person in track(people):
        if (custom_number == None):
            caller_id_resp = api_req(f"people/{person['id']}/features/callerId", method = "put", json = {
                "selected" : caller_id
            })
        else:
            caller_id_resp = api_req(f"people/{person['id']}/features/callerId", method = "put", json = {
                "selected" : caller_id,
                "customNumber" : custom_number
            })

        

    
