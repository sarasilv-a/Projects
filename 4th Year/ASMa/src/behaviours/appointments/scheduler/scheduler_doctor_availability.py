from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import AppointmentMsg
from core.spade_utils import parse_spade_message
from core.utils import logger

class HandleDoctorAvailabilityBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != AppointmentMsg.DOCTOR_AVAILABLE.value:
            return

        sender = str(msg.sender)
        specialty = payload.get("specialty", "general")
        available = bool(payload.get("available", True))

        if available and sender not in self.agent.available_doctors[specialty]:
            self.agent.available_doctors[specialty].append(sender)
            logger.info(f"[SCHED] Doctor available: {sender} specialty={specialty}")
