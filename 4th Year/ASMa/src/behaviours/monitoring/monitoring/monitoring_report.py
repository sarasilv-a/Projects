from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class MonitoringReportBehaviour(PeriodicBehaviour):
    async def run(self):
        active_patients = len(self.agent.history)
        logger.info(
            f"[MONITOR] Report: updates={self.agent.total_updates} alerts={self.agent.total_alerts} patients={active_patients}"
        )
