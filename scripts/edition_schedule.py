"""Fixed editorial edition windows for APURANTE."""
from __future__ import annotations
import datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
UTC=dt.timezone.utc

def config():
 return json.loads((ROOT/'data/edition-schedule.json').read_text())

def parse(value):
 if not value:return None
 parsed=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'))
 return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)

def local_time(at=None):
 cfg=config();zone=ZoneInfo(cfg['timezone']);return (at or dt.datetime.now(UTC)).astimezone(zone)

def slot_for(at=None):
 """Latest scheduled slot at or before *at*, returned in UTC."""
 cfg=config();local=local_time(at);hours=sorted(cfg['slots']);chosen=None
 for hour in hours:
  candidate=local.replace(hour=hour,minute=0,second=0,microsecond=0)
  if candidate<=local:chosen=candidate
 if chosen is None:
  previous=local-dt.timedelta(days=1);chosen=previous.replace(hour=hours[-1],minute=0,second=0,microsecond=0)
 return chosen.astimezone(UTC)

def next_slot(at=None):
 cfg=config();local=local_time(at);hours=sorted(cfg['slots'])
 for hour in hours:
  candidate=local.replace(hour=hour,minute=0,second=0,microsecond=0)
  if candidate>local:return candidate.astimezone(UTC)
 tomorrow=local+dt.timedelta(days=1)
 return tomorrow.replace(hour=hours[0],minute=0,second=0,microsecond=0).astimezone(UTC)

def is_due(state,at=None):
 """True whenever the latest scheduled slot has not been published yet."""
 if state.get('paused'):return False
 current=(at or dt.datetime.now(UTC)).astimezone(UTC);slot=slot_for(current)
 last=parse(state.get('lastEditionSlot'))
 return last is None or last<slot

def slot_iso(at=None):return slot_for(at).isoformat(timespec='seconds').replace('+00:00','Z')

def slot_label(at=None):
 local=slot_for(at).astimezone(ZoneInfo(config()['timezone']))
 return f"Edição das {local.hour:02d}h"

def next_label(at=None):
 current=local_time(at);nxt=next_slot(at).astimezone(ZoneInfo(config()['timezone']))
 day='hoje' if nxt.date()==current.date() else 'amanhã'
 return f"{nxt.hour:02d}h · {day}"
