from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo


def is_nse_open(now: datetime | None = None) -> bool:
    ist = ZoneInfo("Asia/Kolkata")
    now = now.astimezone(ist) if now else datetime.now(ist)
    if now.weekday() >= 5:
        return False
    return time(9, 15) <= now.time() <= time(15, 30)
