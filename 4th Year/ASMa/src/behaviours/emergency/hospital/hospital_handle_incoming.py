from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import Performative, EmergencyMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class HospitalHandleIncomingBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != EmergencyMsg.PATIENT_INCOMING.value:
            return

        sender_transport = str(msg.sender)
        emergency_id = payload.get("emergency_id")
        patient_id = payload.get("patient_id")
        required_specialty = payload.get("required_specialty", "general")

        logger.info(f"[HOSPITAL] Incoming patient from={sender_transport} payload={payload}")

        if not emergency_id:
            return

        if self.agent.has_capacity():
            self.agent.admitted[emergency_id] = {
                "patient_id": patient_id,
                "severity": payload.get("severity"),
                "vitals": payload.get("vitals", {}),
                "required_specialty": required_specialty,
                "arrived_at": get_current_time(),
            }

            confirm_payload = {"emergency_id": emergency_id, "timestamp": get_current_time()}
            confirm = build_spade_message(
                to=sender_transport,
                performative=Performative.CONFIRM,
                msg_type=EmergencyMsg.PATIENT_ADMITTED,
                payload=confirm_payload,
            )
            await self.send(confirm)

        else:
            refuse_payload = {"emergency_id": emergency_id, "status": "hospital_full", "timestamp": get_current_time()}
            refuse = build_spade_message(
                to=sender_transport,
                performative=Performative.REFUSE,
                msg_type=EmergencyMsg.PATIENT_REFUSED,
                payload=refuse_payload,
            )
            await self.send(refuse)
