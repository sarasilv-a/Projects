from __future__ import annotations

from typing import Any, Dict, Optional
from spade.agent import Agent
from spade.template import Template
from core.utils import logger
from core.protocols import EmergencyMsg
from behaviours.emergency.patient.patient_trigger_emergency import TriggerEmergencyBehaviour
from behaviours.emergency.patient.patient_listen_updates import ListenEmergencyUpdatesBehaviour

class PatientAgent(Agent):
    def __init__(self, jid: str, password: str, patient_id: str, name: str):
        super().__init__(jid, password)
        self.patient_id = patient_id
        self.patient_name = name

        self.emergency_id: Optional[str] = None
        self.vitals: Dict[str, Any] = {}
        self.location: Optional[str] = None
        self.status: str = "idle"

    async def setup(self):
        # Disparar emergência
        self.add_behaviour(TriggerEmergencyBehaviour())

        # "Escutar" updates relevantes
        for msg_type in (
            EmergencyMsg.EMERGENCY_ACK.value,
            EmergencyMsg.TRANSPORT_DISPATCHED.value,
            EmergencyMsg.EMERGENCY_RESOLVED.value,
        ):
            tpl = Template()
            tpl.set_metadata("type", msg_type)
            self.add_behaviour(ListenEmergencyUpdatesBehaviour(), tpl)

        logger.info(f"[PATIENT] Agent started: {self.jid}")
