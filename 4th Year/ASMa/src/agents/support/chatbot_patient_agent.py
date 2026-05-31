from __future__ import annotations

from typing import Optional
from spade.agent import Agent
from spade.template import Template
from core.utils import logger
from core.protocols import AppointmentMsg, EmergencyMsg
from behaviours.support.chatbot.chatbot_triage_route import ChatbotTriageRouteBehaviour
from behaviours.support.chatbot.chatbot_listen_replies import ChatbotListenRepliesBehaviour

class ChatbotPatientAgent(Agent):
    def __init__(self, jid: str, password: str, *, patient_id: str = "P001"):
        super().__init__(jid, password)
        self.patient_id = patient_id

        self.appointment_id: Optional[str] = None
        self.emergency_id: Optional[str] = None
        self.status: str = "idle"

    async def setup(self):
        # faz triagem e dispara 1 pedido (consulta ou emergência)
        self.add_behaviour(ChatbotTriageRouteBehaviour())

        # ouve replies de consultas
        for t in (
            AppointmentMsg.APPOINTMENT_QUEUED.value,
            AppointmentMsg.APPOINTMENT_SCHEDULED.value,
            AppointmentMsg.APPOINTMENT_COMPLETED.value,
        ):
            tpl = Template()
            tpl.set_metadata("type", t)
            self.add_behaviour(ChatbotListenRepliesBehaviour(), tpl)

        # ouve replies de emergência
        for t in (
            EmergencyMsg.EMERGENCY_ACK.value,
            EmergencyMsg.TRANSPORT_DISPATCHED.value,
            EmergencyMsg.EMERGENCY_RESOLVED.value,
        ):
            tpl = Template()
            tpl.set_metadata("type", t)
            self.add_behaviour(ChatbotListenRepliesBehaviour(), tpl)

        logger.info(f"[CHATBOT] Agent started: {self.jid} patient_id={self.patient_id}")
