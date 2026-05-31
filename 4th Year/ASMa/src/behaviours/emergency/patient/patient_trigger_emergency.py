from __future__ import annotations

import random
from typing import Any, Dict
from spade.behaviour import OneShotBehaviour
from core.config import EMERGENCY_CENTER_JID
from core.protocols import Performative, EmergencyMsg
from core.spade_utils import build_spade_message
from core.utils import logger, get_current_time, format_emergency_id

class TriggerEmergencyBehaviour(OneShotBehaviour):
    async def run(self):
        agent = self.agent

        agent.location = random.choice(["Braga", "Guimarães", "Viana do Castelo"])
        severity = random.randint(5, 10)
        description = random.choice(["Dor no peito", "Queda grave", "Dificuldade respiratória"])

        agent.vitals = {
            "hr": random.randint(80, 140),
            "spo2": random.randint(85, 98),
            "bp": f"{random.randint(90, 160)}/{random.randint(60, 100)}",
        }

        ts = get_current_time()
        agent.emergency_id = format_emergency_id(agent.patient_id, ts)
        agent.status = "requested"

        payload: Dict[str, Any] = {
            "patient_id": agent.patient_id,
            "patient_name": agent.patient_name,
            "emergency_id": agent.emergency_id,
            "location": agent.location,
            "severity": severity,
            "description": description,
            "vitals": agent.vitals,
            "timestamp": ts,
            "source": "patient",
        }

        msg = build_spade_message(
            to=EMERGENCY_CENTER_JID,
            performative=Performative.REQUEST,
            msg_type=EmergencyMsg.EMERGENCY_ALERT,
            payload=payload,
        )

        logger.info(f"[PATIENT] REQUEST emergency_alert: {payload}")
        await self.send(msg)
