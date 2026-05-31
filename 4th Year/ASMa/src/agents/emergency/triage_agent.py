from __future__ import annotations

from spade.agent import Agent
from spade.template import Template
from core.protocols import EmergencyMsg
from core.utils import logger
from behaviours.emergency.triage.triage_receive_case import ReceiveTriageCaseBehaviour
from behaviours.emergency.triage.triage_report import TriageReportBehaviour


class TriageAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self.total_cases = 0

    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", EmergencyMsg.TRIAGE_CASE.value)
        self.add_behaviour(ReceiveTriageCaseBehaviour(), tpl)

        self.add_behaviour(TriageReportBehaviour(period=10))

        logger.info(f"[TRIAGE] Agent started: {self.jid}")
