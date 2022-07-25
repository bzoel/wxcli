"""
wxtcli - people.py
Billy Zoellers

People module
"""
import typer
from wxtcli.console import console
from wxtcli.api import api
from wxtcli.helpers.formatting import table_with_columns, humanize_wxt_datetime
from rich.progress import track

app = typer.Typer()

@app.command()
def template(
):
    """
    A template function
    """
    console.print("Hi")
