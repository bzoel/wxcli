"""
wxtcli - voicemail.py
David Rice

Voicemail module
"""
import typer
from wxcli.console import console
from wxcli.api import api_req
from wxcli.helpers.formatting import table_with_columns
from rich.progress import track

app = typer.Typer()


@app.command()
def list_voicemail_settings(
    location_name: str = typer.Option(None, help="Webex Calling Location Name"),
    org_id: str = typer.Option(None, help="Organization ID"),
):
    """
    List Voicemail settings for all people (in a location, if specified)
    """
    orgId = None
    if org_id is not None:
        orgId = api_req(f"organizations/{org_id}")["id"]

    people = []
    if location_name is not None:
        # First locationId of interest
        if org_id is not None:
            locations = api_req(
                "locations",
                params={
                    "orgId": org_id,
                },
            )
        else:
            locations = api_req("locations")
        locationId = next(
            location["id"]
            for location in locations
            if location["name"] == location_name
        )

        # Find people belonging to that locationId
        if orgId is not None:
            people = api_req(
                "people",
                params={
                    "callingData": True,
                    "locationId": locationId,
                    "orgId": orgId,
                },
            )
        else:
            people = api_req(
                "people",
                params={
                    "callingData": True,
                    "locationId": locationId,
                },
            )
    else:
        # Find people belonging to all locationId's (avoids dealing with non-WxC Users)
        locations = api_req("locations")
        for location in locations:
            people = people + api_req(
                "people", params={"callingData": True, "locationId": location["id"]}
            )

    # Find callerId for each person
    table = table_with_columns(
        [
            "Person",
            "Extension",
            "VM Enabled",
            "Send Busy",
            "SendNoAnswer",
            "Notifications",
            "EmailVM",
            "Email Address",
            "Storage",
        ],
        title="Voicemail Info",
    )
    for person in track(people):
        if org_id is not None:
            voicemail_info = api_req(
                f"people/{person['id']}/features/voicemail", params={"orgId": orgId}
            )
        else:
            voicemail_info = api_req(f"people/{person['id']}/features/voicemail")

        table.add_row(
            person["displayName"],
            person["extension"],
            "Yes" if voicemail_info["enabled"] else "No",
            "Yes" if voicemail_info["sendBusyCalls"]["enabled"] else "No",
            "Yes" if voicemail_info["sendUnansweredCalls"]["enabled"] else "No",
            "Yes" if voicemail_info["notifications"]["enabled"] else "No",
            "Yes" if voicemail_info["emailCopyOfMessage"]["enabled"] else "No",
            voicemail_info["emailCopyOfMessage"]["emailId"]
            if voicemail_info["emailCopyOfMessage"]["enabled"]
            else "N/A",
            voicemail_info["messageStorage"]["storageType"],
        )
    console.print(table)


@app.command()
def update_allvms(
    location_name: str = typer.Option(None, help="Webex Calling Location Name"),
    org_id: str = typer.Option(None, help="Organization ID"),
):
    """
    Update Voicemail To Email for all people in a location to their Webex Email Address
    """
    orgId = None
    if org_id is not None:
        orgId = api_req(f"organizations/{org_id}")["id"]

    # First locationId of interest
    if org_id is not None:
        locations = api_req(
            "locations",
            params={
                "orgId": org_id,
            },
        )
    else:
        locations = api_req("locations")
    locationId = next(
        location["id"] for location in locations if location["name"] == location_name
    )

    # Find people belonging to that locationId
    if orgId is not None:
        people = api_req(
            "people",
            params={
                "callingData": True,
                "locationId": locationId,
                "orgId": orgId,
            },
        )
    else:
        people = api_req(
            "people",
            params={
                "callingData": True,
                "locationId": locationId,
            },
        )

    # Set Voicemai to Email for each person

    for person in track(people):
        if org_id is not None:
            api_req(
                f"people/{person['id']}/features/voicemail",
                method="put",
                json={
                    "emailCopyOfMessage": {
                        "enabled": True,
                        "emailId": person["emails"][0],
                    }
                },
                params={
                    "orgId": orgId,
                },
            )
        else:
            api_req(
                f"people/{person['id']}/features/voicemail",
                method="put",
                json={
                    "emailCopyOfMessage": {
                        "enabled": True,
                        "emailId": person["emails"][0],
                    }
                },
            )
