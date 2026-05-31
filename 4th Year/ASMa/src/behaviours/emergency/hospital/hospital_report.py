from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class HospitalReportBehaviour(PeriodicBehaviour):
    async def run(self):
        logger.info(f"[HOSPITAL] Report: admitted={len(self.agent.admitted)}/{self.agent.capacity}")
