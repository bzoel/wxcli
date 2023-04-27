"""
wxtcli - rooms.py
Billy Zoellers

Rooms module
"""
import typer
from typing import Optional
from enum import Enum
from wxcli.console import console
from wxcli.api import api
from wxcli.helpers.formatting import table_with_columns, humanize_wxt_datetime

app = typer.Typer()

class RoomType(str, Enum):
  """
  Types of Webex Rooms
  """
  direct = "direct"
  group = "group"

class RoomSort(str, Enum):
  """
  Sort options of Webex Rooms
  """
  id = "id"
  lastactivity = "lastactivity"
  created = "created"

@app.command()
def list(
  type: Optional[RoomType] = None,
  sort: Optional[RoomSort] = None
):
  """
  List Rooms
  """
  # Enumerate arguments
  args = {}
  if type is not None:
    args["type"] = type.value
  if sort is not None:
    args["sortBy"] = sort.value

  rooms = api.rooms.list(**args)

  # Create and display a table with results
  table = table_with_columns(
    columns=["Name", "Type", "Locked", "Last Activity", "Created"],
    title="Teams"
  )
  for room in rooms:
    table.add_row(
      room.title,
      room.type,
      "Locked" if room.isLocked else "Not Locked",
      humanize_wxt_datetime(room.lastActivity),
      humanize_wxt_datetime(room.created)
    )
  console.print(table)