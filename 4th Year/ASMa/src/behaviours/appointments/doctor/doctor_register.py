from __future__ import annotations

from spade.behaviour import OneShotBehaviour
from core.config import SCHEDULER_JID
from core.protocols import Performative, AppointmentMsg
from core.spade_utils import build_spade_message
from core.utils import logger, get_current_time

class DoctorRegisterBehaviour(OneShotBehaviour):
    async def run(self):
        payload = {
            "doctor_jid": str(self.agent.jid),
            "specialty": self.agent.specialty,
            "available": self.agent.available,
            "timestamp": get_current_time(),
        }
        msg = build_spade_message(
            to=SCHEDULER_JID,
            performative=Performative.INFORM,
            msg_type=AppointmentMsg.DOCTOR_AVAILABLE,
            payload=payload,
        )
        await self.send(msg)
        logger.info(f"[DOCTOR] Registered availability: {payload}")
    