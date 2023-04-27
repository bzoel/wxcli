"""
wxtcli - people.py
Billy Zoellers

People module
"""
import typer
from typing import Optional
from enum import Enum
from wxcli.console import console
from wxcli.api import api
from wxcli.helpers.formatting import table_with_columns, humanize_wxt_datetime
from rich.progress import track

app = typer.Typer()

@app.command()
def list(
  org_name: Optional[str] = None,
  filter_emaildomain: Optional[str] = None,
):
  args = {
    "max": 1000
  }
  # Find org ID to filter by if specified
  if org_name is not None:
    orgs = api.organizations.list()
    try:
      org = next(org for org in orgs if org.displayName == org_name)
      args["orgId"] = org.id
    except StopIteration:
      console.print(f"Org named [bold]{org_name}[/bold] was not found.")
      raise typer.Abort()

  # Get list of people and filter if needed
  people = api.people.list(**args)
  if filter_emaildomain is not None:
    people = [person for person in people if f"@{filter_emaildomain}" in person.emails[0]]

  table = table_with_columns(["Name", "Email", "Created", "Invite Pending", "Login Enabled"], title="People")
  for p in people:
    table.add_row(
      p.displayName,
      p.emails[0],
      humanize_wxt_datetime(p.created),
      "Yes" if p.invitePending else "No",
      "Yes" if p.loginEnabled else "No"
    )
  console.print(table)

@app.command()
def create_team_membership_by_emaildomain(
  team_name: str,
  org_name: str,
  people_emaildomain: Optional[str] = None
):
  """
  Add 1 or more people to a room or team
  """
  people_args = {
    "max": 1000
  }
  # Find org
  orgs = api.organizations.list()
  try:
    org = next(org for org in orgs if org.displayName == org_name)
    people_args["orgId"] = org.id
  except StopIteration:
    console.print(f"Org named [bold]{org_name}[/bold] was not found.")
    raise typer.Abort()

  # Get list of people and filter if needed
  people = api.people.list(**people_args)
  if people_emaildomain is not None:
    people = [person for person in people if f"@{people_emaildomain}" in person.emails[0]]
  else:
    people = [person for person in people]
  # Find team
  teams = api.teams.list()
  try:
    team = next(team for team in teams if team.name == team_name)
  except StopIteration:
    console.print(f"Team named [bold]{team_name}[/bold] was not found.")
    raise typer.Abort()

  # Find existing team memberships
  team_memberships = api.team_memberships.list(teamId=team.id, max=1000)
  team_memberships = [m for m in team_memberships]
  # Create new memberships if they do not already exist
  for p in people:
    if not any(tm for tm in team_memberships if p.id == tm.personId):
      new_tm = api.team_memberships.create(teamId=team.id, personId=p.id)
      console.log(f" [green][bold]{p.displayName}[/bold] has been added to [bold]{team.name}[/bold]")
    else:
      console.log(f" [bold]{p.displayName}[/bold] is already a member of [bold]{team.name}[/bold]")

@app.command()
def create_room_membership_by_emaildomain(
  room_name: str,
  org_name: str,
  people_emaildomain: Optional[str] = None
):
  """
  Add 1 or more people to a room
  """
  people_args = {
    "max": 1000
  }
  # Find org
  orgs = api.organizations.list()
  
  org = next(org for org in orgs if org.displayName == org_name)
  people_args["orgId"] = org.id
  console.log(org)

  # Get list of people and filter if needed
  people = api.people.list(**people_args)
  if people_emaildomain is not None:
    people = [person for person in people if f"@{people_emaildomain}" in person.emails[0]]
  else:
    people = [p for p in people]

  # Find team
  rooms = api.rooms.list()
  try:
    room = next(room for room in rooms if room.title == room_name)
  except StopIteration:
    console.print(f"Room named [bold]{room_name}[/bold] was not found.")
    raise typer.Abort()
  console.log(room)
  # Find existing team memberships
  memberships = api.memberships.list(roomId=room.id, max=1000)
  memberships = [m for m in memberships]

  # Create new memberships if they do not already exist
  for p in track(people, console=console):
    if not any(m for m in memberships if p.id == m.personId):
      new_tm = api.memberships.create(roomId=room.id, personId=p.id)
      console.log(f" [green][bold]{p.displayName}[/bold] has been added to [bold]{room.title}[/bold]")
    else:
      console.log(f" [bold]{p.displayName}[/bold] is already a member of [bold]{room.title}[/bold]")
