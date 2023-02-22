"""
wxtcli - main.py
Billy Zoellers

A CLI application based on Typer for interating with Cisco Webex (Teams)
"""
import typer
from wxtcli.console import console
from wxtcli import rooms, people, teams, calling, voicemail, workspace

def create_wxt():
  """
  Typer callback to create session to Webex Teams
  """

app = typer.Typer()
app.add_typer(rooms.app, name="rooms")
app.add_typer(people.app, name="people")
app.add_typer(teams.app, name="teams")
app.add_typer(calling.app, name="calling")
app.add_typer(voicemail.app, name="voicemail")
app.add_typer(workspace.app, name="workspace")
