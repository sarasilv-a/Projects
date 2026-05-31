from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.utils import logger

class SchedulerReportBehaviour(PeriodicBehaviour):
    async def run(self):
        pending_total = sum(len(q) for q in self.agent.pending.values())
        available_total = sum(len(lst) for lst in self.agent.available_doctors.values())
        logger.info(
            f"[SCHED] Report: requests={self.agent.total_requests} scheduled={self.agent.total_scheduled} "
            f"completed={self.agent.total_completed} pending={pending_total} available_doctors={available_total}"
        )
