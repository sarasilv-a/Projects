from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class CenterReportBehaviour(PeriodicBehaviour):
    async def run(self):
        logger.info(f"[CENTER] Report: active_emergencies={len(self.agent.active_emergencies)}")
