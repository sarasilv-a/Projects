from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class DoctorReportBehaviour(PeriodicBehaviour):
    async def run(self):
        logger.info(f"[DOCTOR] Report: specialty={self.agent.specialty} total={self.agent.total_consultations} available={self.agent.available}")
