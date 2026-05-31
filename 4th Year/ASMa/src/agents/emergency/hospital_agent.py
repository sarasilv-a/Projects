from __future__ import annotations

from typing import Any, Dict
from spade.agent import Agent
from spade.template import Template
from core.protocols import EmergencyMsg, SpecialistMsg
from core.utils import logger
from behaviours.emergency.hospital.hospital_handle_incoming import HospitalHandleIncomingBehaviour
from behaviours.emergency.hospital.hospital_specialist_flow import HospitalSpecialistFlowBehaviour
from behaviours.emergency.hospital.hospital_report import HospitalReportBehaviour
from behaviours.emergency.hospital.hospital_handle_treatment_update import HospitalHandleTreatmentUpdateBehaviour

class HospitalAgent(Agent):
    def __init__(self, jid: str, password: str, *, capacity: int = 5):
        super().__init__(jid, password)
        self.capacity = capacity
        self.admitted: Dict[str, Dict[str, Any]] = {}

    def has_capacity(self) -> bool:
        return len(self.admitted) < self.capacity

    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", EmergencyMsg.PATIENT_INCOMING.value)
        self.add_behaviour(HospitalHandleIncomingBehaviour(), tpl)

        self.add_behaviour(HospitalSpecialistFlowBehaviour(period=5))

        self.add_behaviour(HospitalReportBehaviour(period=10))

        tpl3 = Template()
        tpl3.set_metadata("type", SpecialistMsg.TREATMENT_UPDATE.value)
        self.add_behaviour(HospitalHandleTreatmentUpdateBehaviour(), tpl3)

        logger.info(f"[HOSPITAL] Agent started: {self.jid}")
