"""
wxtcli - teams.py
Billy Zoellers

Teams module
"""
import typer
from wxcli.console import console
from wxcli.api import api
from wxcli.helpers.formatting import table_with_columns

app = typer.Typer()


@app.command()
def list():
    """
    List Teams
    """
    teams = api.teams.list()

    table = table_with_columns(columns=["Name", "ID"], title="Teams")
    for team in teams:
        table.add_row(team.name, team.id)
    console.print(table)
