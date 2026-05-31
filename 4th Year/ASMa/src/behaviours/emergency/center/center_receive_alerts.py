from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.config import jid
from core.protocols import Performative, EmergencyMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time
from core.config import TRIAGE_JID


class ReceiveEmergencyAlertsBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != EmergencyMsg.EMERGENCY_ALERT.value:
            return

        sender = str(msg.sender)
        emergency_id = payload.get("emergency_id")
        patient_id = payload.get("patient_id")

        logger.info(f"[CENTER] Received emergency_alert from={sender} payload={payload}")

        # registo
        self.agent.active_emergencies[emergency_id] = {
            "patient_jid": sender,
            "patient_id": patient_id,
            "payload": payload,
            "status": "received",
            "created_at": get_current_time(),
        }

        # ACK ao paciente/origem
        ack_payload = {
            "emergency_id": emergency_id,
            "status": "acknowledged",
            "timestamp": get_current_time(),
        }
        ack = build_spade_message(
            to=sender,
            performative=Performative.INFORM,
            msg_type=EmergencyMsg.EMERGENCY_ACK,
            payload=ack_payload,
        )
        await self.send(ack)

        # pedir triagem
        triage_payload = {
            "emergency_id": emergency_id,
            "patient_id": patient_id,
            "description": payload.get("description"),
            "severity": payload.get("severity"),
            "vitals": payload.get("vitals", {}),
            "timestamp": get_current_time(),
        }
        triage_msg = build_spade_message(
            to=TRIAGE_JID,
            performative=Performative.REQUEST,
            msg_type=EmergencyMsg.TRIAGE_CASE,
            payload=triage_payload,
        )
        await self.send(triage_msg)

        # marcar estado
        self.agent.active_emergencies[emergency_id]["status"] = "triage_requested"
