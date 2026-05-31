from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class AmbulanceReportBehaviour(PeriodicBehaviour):
    async def run(self):
        logger.info(f"[AMBULANCE] Report: total_jobs={self.agent.total_jobs} available={self.agent.available}")
