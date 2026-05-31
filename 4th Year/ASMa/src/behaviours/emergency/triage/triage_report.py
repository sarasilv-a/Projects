from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class TriageReportBehaviour(PeriodicBehaviour):
    async def run(self):
        logger.info(f"[TRIAGE] Report: total_cases={self.agent.total_cases}")
