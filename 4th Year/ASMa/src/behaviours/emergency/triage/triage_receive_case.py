from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import Performative, EmergencyMsg, TransportType, MedicalSpecialty
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class ReceiveTriageCaseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != EmergencyMsg.TRIAGE_CASE.value:
            return

        self.agent.total_cases += 1

        emergency_id = payload.get("emergency_id", "")
        severity = int(payload.get("severity", 5))
        description = (payload.get("description") or "").lower()
        vitals = payload.get("vitals", {})

        # regras simples para decidir transporte e especialidade
        spo2 = int(vitals.get("spo2", 99)) if isinstance(vitals.get("spo2", 99), int) else 99
        hr = int(vitals.get("hr", 80)) if isinstance(vitals.get("hr", 80), int) else 80

        # transporte
        transport = TransportType.HELICOPTER if (severity >= 9 or spo2 < 88) else TransportType.AMBULANCE

        # especialidade
        if "peito" in description or hr > 130:
            specialty = MedicalSpecialty.CARDIOLOGY
        elif "queda" in description:
            specialty = MedicalSpecialty.ORTHOPEDICS
        elif "respirat" in description or spo2 < 90:
            specialty = MedicalSpecialty.GENERAL
        else:
            specialty = MedicalSpecialty.GENERAL

        result_payload = {
            "emergency_id": emergency_id,
            "severity": severity,
            "priority": severity,  # simples
            "transport_type": transport.value,
            "required_specialty": specialty.value,
            "timestamp": get_current_time(),
        }

        # responder para quem pediu triagem (sender = EmergencyCenter)
        reply = build_spade_message(
            to=str(msg.sender),
            performative=Performative.INFORM,
            msg_type=EmergencyMsg.TRIAGE_RESULT,
            payload=result_payload,
        )

        logger.info(f"[TRIAGE] INFORM triage_result: {result_payload}")
        await self.send(reply)
