from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import Performative, EmergencyMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class HandleStatusQueriesBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != EmergencyMsg.EMERGENCY_STATUS_REQ.value:
            return

        sender = str(msg.sender)
        emergency_id = payload.get("emergency_id")
        rec = self.agent.active_emergencies.get(emergency_id)

        status_payload = {
            "emergency_id": emergency_id,
            "exists": rec is not None,
            "status": rec.get("status") if rec else "unknown",
            "timestamp": get_current_time(),
        }

        reply = build_spade_message(
            to=sender,
            performative=Performative.INFORM,
            msg_type=EmergencyMsg.EMERGENCY_STATUS,
            payload=status_payload,
        )
        await self.send(reply)
