from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import EmergencyMsg
from core.spade_utils import parse_spade_message
from core.utils import logger

class ListenEmergencyUpdatesBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        logger.info(f"[PATIENT] Received perf={perf} type={mtype} payload={payload}")

        if mtype == EmergencyMsg.EMERGENCY_ACK.value:
            self.agent.status = "acknowledged"

        elif mtype == EmergencyMsg.TRANSPORT_DISPATCHED.value:
            self.agent.status = "transport_dispatched"

        elif mtype == EmergencyMsg.EMERGENCY_RESOLVED.value:
            self.agent.status = "resolved"
            logger.info("[PATIENT] Emergency resolved. Stopping agent.")
            await self.agent.stop()
