"""
wxtcli - main.py
Billy Zoellers

A CLI application based on Typer for interating with Cisco Webex (Teams)
"""
import typer
from wxtcli.console import console
from wxtcli import rooms, people, teams

def create_wxt():
  """
  Typer callback to create session to Webex Teams
  """

app = typer.Typer()
app.add_typer(rooms.app, name="rooms")
app.add_typer(people.app, name="people")
app.add_typer(teams.app, name="teams")