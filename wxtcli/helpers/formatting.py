"""
wxtcli - formatting.py
Billy Zoellers

formatting helpers
"""
from rich import box
from rich.table import Table
from webexteamssdk import WebexTeamsDateTime
import humanize
from datetime import datetime, timedelta
from wxtcli.console import console


def table_with_columns(columns: list, title: str) -> Table:
  table = Table(*columns, title=title, box=box.ROUNDED)

  return table

def humanize_wxt_datetime(dt: WebexTeamsDateTime) -> str:
  dt_now = datetime.utcnow()
  dt_obj = datetime.fromisoformat(str(dt).rstrip("Z"))
  return humanize.naturaldelta(dt_now - dt_obj)