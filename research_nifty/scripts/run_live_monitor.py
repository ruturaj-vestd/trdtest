from __future__ import annotations

import asyncio

from services.monitoring import run_live_monitor


if __name__ == "__main__":
    asyncio.run(run_live_monitor())
