from __future__ import annotations

from typing import Optional
from spade.agent import Agent
from spade.template import Template
from core.protocols import EmergencyMsg
from core.utils import logger
from behaviours.emergency.ambulance.ambulance_handle_dispatch import AmbulanceHandleDispatchBehaviour
from behaviours.emergency.ambulance.ambulance_hospital_reply import AmbulanceHospitalReplyBehaviour
from behaviours.emergency.ambulance.ambulance_report import AmbulanceReportBehaviour

class AmbulanceAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self.available: bool = True
        self.current_emergency_id: Optional[str] = None
        self.total_jobs: int = 0
        self.center_jid: Optional[str] = None

    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", EmergencyMsg.TRANSPORT_DISPATCH.value)
        self.add_behaviour(AmbulanceHandleDispatchBehaviour(), tpl)

        for t in (EmergencyMsg.PATIENT_ADMITTED.value, EmergencyMsg.PATIENT_REFUSED.value):
            tpl2 = Template()
            tpl2.set_metadata("type", t)
            self.add_behaviour(AmbulanceHospitalReplyBehaviour(), tpl2)

        self.add_behaviour(AmbulanceReportBehaviour(period=10))
        logger.info(f"[AMBULANCE] Agent started: {self.jid}")
