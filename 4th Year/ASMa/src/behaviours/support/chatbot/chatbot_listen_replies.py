from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import AppointmentMsg, EmergencyMsg
from core.spade_utils import parse_spade_message
from core.utils import logger

class ChatbotListenRepliesBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=20)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        logger.info(f"[CHATBOT] Received perf={perf} type={mtype} payload={payload}")

        # Consultas
        if mtype == AppointmentMsg.APPOINTMENT_QUEUED.value:
            self.agent.status = "queued"

        elif mtype == AppointmentMsg.APPOINTMENT_SCHEDULED.value:
            self.agent.status = "scheduled"

        elif mtype == AppointmentMsg.APPOINTMENT_COMPLETED.value:
            self.agent.status = "completed"
            logger.info("[CHATBOT] Appointment completed. Stopping agent.")
            await self.agent.stop()

        # Emergência
        elif mtype == EmergencyMsg.EMERGENCY_ACK.value:
            self.agent.status = "emergency_acknowledged"

        elif mtype == EmergencyMsg.TRANSPORT_DISPATCHED.value:
            self.agent.status = "transport_dispatched"

        elif mtype == EmergencyMsg.EMERGENCY_RESOLVED.value:
            self.agent.status = "emergency_resolved"
            logger.info("[CHATBOT] Emergency resolved. Stopping agent.")
            await self.agent.stop()
