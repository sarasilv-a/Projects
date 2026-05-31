from __future__ import annotations

import random
from typing import Any, Dict
from spade.behaviour import OneShotBehaviour
from core.config import SCHEDULER_JID, EMERGENCY_CENTER_JID
from core.protocols import Performative, AppointmentMsg, EmergencyMsg, MedicalSpecialty
from core.spade_utils import build_spade_message
from core.utils import logger, get_current_time

class ChatbotTriageRouteBehaviour(OneShotBehaviour):
    async def run(self):
        # Simular input do utilizador
        symptoms = random.choice([
            "consulta rotina",
            "renovar receita",
            "dor leve",
            "dor no peito",
            "dificuldade respiratória",
            "desmaio",
        ])

        urgent_keywords = {"dor no peito", "dificuldade respiratória", "desmaio", "hemorragia"}
        is_urgent = symptoms in urgent_keywords

        if is_urgent:
            # -> Emergência
            self.agent.emergency_id = f"EMG-{self.agent.patient_id}-{random.randint(1000,9999)}"

            payload: Dict[str, Any] = {
                "patient_id": self.agent.patient_id,
                "patient_name": f"Patient {self.agent.patient_id}",
                "emergency_id": self.agent.emergency_id,
                "location": "UNKNOWN",
                "severity": 9,
                "description": f"Chatbot triage urgent: {symptoms}",
                "vitals": {},
                "timestamp": get_current_time(),
                "source": "chatbot_triage",
            }

            msg = build_spade_message(
                to=EMERGENCY_CENTER_JID,
                performative=Performative.REQUEST,
                msg_type=EmergencyMsg.EMERGENCY_ALERT,
                payload=payload,
            )
            await self.send(msg)
            self.agent.status = "emergency_requested"
            logger.warning(f"[CHATBOT] TRIAGE URGENT -> emergency_alert: {payload}")

        else:
            # Marcação
            self.agent.appointment_id = f"APT-{self.agent.patient_id}-{random.randint(1000,9999)}"

            # heurística simples de especialidade
            if "peito" in symptoms:
                specialty = MedicalSpecialty.CARDIOLOGY.value
            else:
                specialty = random.choice([
                    MedicalSpecialty.GENERAL.value,
                    MedicalSpecialty.DERMATOLOGY.value,
                    MedicalSpecialty.CARDIOLOGY.value,
                ])

            payload = {
                "appointment_id": self.agent.appointment_id,
                "patient_id": self.agent.patient_id,
                "specialty": specialty,
                "reason": f"Chatbot triage non-urgent: {symptoms}",
                "timestamp": get_current_time(),
            }

            msg = build_spade_message(
                to=SCHEDULER_JID,
                performative=Performative.REQUEST,
                msg_type=AppointmentMsg.APPOINTMENT_REQUEST,
                payload=payload,
            )
            await self.send(msg)
            self.agent.status = "appointment_requested"
            logger.info(f"[CHATBOT] TRIAGE NON-URGENT -> appointment_request: {payload}")
