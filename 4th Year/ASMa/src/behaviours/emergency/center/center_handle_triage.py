from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.config import AMBULANCE_JIDS, HELICOPTER_JIDS, HOSPITAL_JIDS
from core.protocols import Performative, EmergencyMsg, TransportType
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class HandleTriageResultBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        _perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != EmergencyMsg.TRIAGE_RESULT.value:
            return

        emergency_id = payload.get("emergency_id")
        if emergency_id not in self.agent.active_emergencies:
            logger.warning(f"[CENTER] triage_result for unknown emergency_id: {payload}")
            return

        rec = self.agent.active_emergencies[emergency_id]
        rec["triage"] = payload
        rec["status"] = "triaged"

        patient_jid = rec["patient_jid"]
        base = rec["payload"]

        transport_type = payload.get("transport_type", TransportType.AMBULANCE.value)
        required_specialty = payload.get("required_specialty", "general")

        # escolher hospital (RR) + guardar tentativas
        rec.setdefault("tried_hospitals", [])
        hospital_jid = self.agent.pick_hospital(HOSPITAL_JIDS, avoid=rec["tried_hospitals"])
        if hospital_jid:
            rec["tried_hospitals"].append(hospital_jid)
        else:
            # sem hospital -> fica pendente
            rec["status"] = "awaiting_capacity"
            logger.warning(f"[CENTER] No hospitals available for emergency_id={emergency_id}")
            return

        # escolher transport (RR)
        if transport_type == TransportType.AMBULANCE.value:
            transport_jid = self.agent.pick_ambulance(AMBULANCE_JIDS)
        else:
            transport_jid = self.agent.pick_helicopter(HELICOPTER_JIDS)

        if not transport_jid:
            rec["status"] = "awaiting_transport"
            logger.warning(f"[CENTER] No transport available for emergency_id={emergency_id}")
            return

        rec["transport_type"] = transport_type
        rec["transport_jid"] = transport_jid
        rec["hospital_jid"] = hospital_jid
        rec["required_specialty"] = required_specialty

        dispatch_payload = {
            "emergency_id": emergency_id,
            "patient_id": base.get("patient_id"),
            "patient_jid": patient_jid,
            "location": base.get("location"),
            "severity": base.get("severity"),
            "vitals": base.get("vitals", {}),
            "transport_type": transport_type,
            "required_specialty": required_specialty,
            "hospital_jid": hospital_jid,
            "timestamp": get_current_time(),
        }

        dispatch = build_spade_message(
            to=transport_jid,
            performative=Performative.REQUEST,
            msg_type=EmergencyMsg.TRANSPORT_DISPATCH,
            payload=dispatch_payload,
        )
        await self.send(dispatch)

        # informar paciente que foi despachado transporte
        info_payload = {
            "emergency_id": emergency_id,
            "transport_type": transport_type,
            "status": "transport_dispatched",
            "timestamp": get_current_time(),
        }
        info = build_spade_message(
            to=patient_jid,
            performative=Performative.INFORM,
            msg_type=EmergencyMsg.TRANSPORT_DISPATCHED,
            payload=info_payload,
        )
        await self.send(info)

        rec["status"] = "dispatched"
        logger.info(f"[CENTER] Dispatched transport={transport_type} to={transport_jid} hospital={hospital_jid} emergency_id={emergency_id}")
