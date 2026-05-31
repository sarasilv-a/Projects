from __future__ import annotations

from typing import Optional
from spade.agent import Agent
from spade.template import Template
from core.protocols import EmergencyMsg
from core.utils import logger
from behaviours.emergency.helicopter.helicopter_handle_dispatch import HelicopterHandleDispatchBehaviour
from behaviours.emergency.helicopter.helicopter_hospital_reply import HelicopterHospitalReplyBehaviour
from behaviours.emergency.helicopter.helicopter_report import HelicopterReportBehaviour

class HelicopterAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self.available: bool = True
        self.current_emergency_id: Optional[str] = None
        self.total_jobs: int = 0
        self.center_jid: Optional[str] = None

    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", EmergencyMsg.TRANSPORT_DISPATCH.value)
        self.add_behaviour(HelicopterHandleDispatchBehaviour(), tpl)

        for t in (EmergencyMsg.PATIENT_ADMITTED.value, EmergencyMsg.PATIENT_REFUSED.value):
            tpl2 = Template()
            tpl2.set_metadata("type", t)
            self.add_behaviour(HelicopterHospitalReplyBehaviour(), tpl2)

        self.add_behaviour(HelicopterReportBehaviour(period=10))
        logger.info(f"[HELICOPTER] Agent started: {self.jid}")
