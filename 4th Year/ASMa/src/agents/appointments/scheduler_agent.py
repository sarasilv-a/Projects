from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Deque, Dict, List
from spade.agent import Agent
from spade.template import Template
from core.protocols import AppointmentMsg
from core.utils import logger
from behaviours.appointments.scheduler.scheduler_receive_requests import ReceiveAppointmentRequestsBehaviour, ReceiveSpecialistRequestsBehaviour
from behaviours.appointments.scheduler.scheduler_doctor_availability import HandleDoctorAvailabilityBehaviour
from behaviours.appointments.scheduler.scheduler_doctor_done import HandleDoctorDoneBehaviour
from behaviours.appointments.scheduler.scheduler_report import SchedulerReportBehaviour

class SchedulerAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)

        self.pending: Dict[str, Deque[Dict[str, Any]]] = defaultdict(deque)
        self.available_doctors: Dict[str, List[str]] = defaultdict(list)
        self.active: Dict[str, Dict[str, Any]] = {}

        self.total_requests = 0
        self.total_scheduled = 0
        self.total_completed = 0

    def try_assign(self, specialty: str):
        if not self.pending[specialty]:
            return None
        if not self.available_doctors[specialty]:
            return None

        req = self.pending[specialty].popleft()
        doctor_jid = self.available_doctors[specialty].pop(0)

        appointment_id = req["appointment_id"]
        patient_jid = req["patient_jid"]

        self.active[appointment_id] = {
            "patient_jid": patient_jid,
            "doctor_jid": doctor_jid,
            "specialty": specialty,
            "status": "assigned",
        }

        return req, doctor_jid

    async def setup(self):
        # appointment_request
        tpl1 = Template()
        tpl1.set_metadata("type", AppointmentMsg.APPOINTMENT_REQUEST.value)
        self.add_behaviour(ReceiveAppointmentRequestsBehaviour(), tpl1)

        # doctor_available
        tpl2 = Template()
        tpl2.set_metadata("type", AppointmentMsg.DOCTOR_AVAILABLE.value)
        self.add_behaviour(HandleDoctorAvailabilityBehaviour(), tpl2)

        # doctor_done
        tpl3 = Template()
        tpl3.set_metadata("type", AppointmentMsg.DOCTOR_DONE.value)
        self.add_behaviour(HandleDoctorDoneBehaviour(), tpl3)

        # specialist_request
        from core.protocols import SpecialistMsg
        tpl4 = Template()
        tpl4.set_metadata("type", SpecialistMsg.SPECIALIST_REQUEST.value)
        self.add_behaviour(ReceiveSpecialistRequestsBehaviour(), tpl4)

        self.add_behaviour(SchedulerReportBehaviour(period=10))

        logger.info(f"[SCHED] Agent started: {self.jid}")
