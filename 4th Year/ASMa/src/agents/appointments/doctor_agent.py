from __future__ import annotations

from typing import Optional
from spade.agent import Agent
from spade.template import Template
from core.protocols import AppointmentMsg
from core.utils import logger
from behaviours.appointments.doctor.doctor_register import DoctorRegisterBehaviour
from behaviours.appointments.doctor.doctor_handle_assignment import DoctorHandleAssignmentBehaviour
from behaviours.appointments.doctor.doctor_report import DoctorReportBehaviour

class DoctorAgent(Agent):
    def __init__(self, jid: str, password: str, *, specialty: str):
        super().__init__(jid, password)
        self.specialty = specialty
        self.available: bool = True
        self.total_consultations: int = 0
        self.current_appointment_id: Optional[str] = None

    async def setup(self):
        self.add_behaviour(DoctorRegisterBehaviour())

        tpl = Template()
        tpl.set_metadata("type", AppointmentMsg.DOCTOR_ASSIGN.value)
        self.add_behaviour(DoctorHandleAssignmentBehaviour(), tpl)

        self.add_behaviour(DoctorReportBehaviour(period=10))
        logger.info(f"[DOCTOR] Agent started: {self.jid} specialty={self.specialty}")
