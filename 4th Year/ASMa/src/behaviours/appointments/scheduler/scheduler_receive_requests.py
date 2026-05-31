from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import Performative, AppointmentMsg, SpecialistMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class ReceiveAppointmentRequestsBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != AppointmentMsg.APPOINTMENT_REQUEST.value:
            return

        sender = str(msg.sender)
        specialty = payload.get("specialty", "general")
        appointment_id = payload.get("appointment_id")
        reason = payload.get("reason", "")

        self.agent.total_requests += 1

        self.agent.pending[specialty].append(
            {
                "appointment_id": appointment_id,
                "patient_jid": sender,
                "specialty": specialty,
                "reason": reason,
                "timestamp": payload.get("timestamp", get_current_time()),
                "mode": "appointment",
            }
        )

        # queued reply
        ack_payload = {"appointment_id": appointment_id, "status": "queued", "specialty": specialty, "timestamp": get_current_time()}
        ack = build_spade_message(
            to=sender,
            performative=Performative.INFORM,
            msg_type=AppointmentMsg.APPOINTMENT_QUEUED,
            payload=ack_payload,
        )
        await self.send(ack)

        await _try_assign_and_send(self)


class ReceiveSpecialistRequestsBehaviour(CyclicBehaviour):
    """
    Recebe REQUEST specialist_request do hospital e trata como um pedido por especialidade.
    """
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != SpecialistMsg.SPECIALIST_REQUEST.value:
            return

        hospital_jid = str(msg.sender)
        emergency_id = payload.get("emergency_id")
        specialty = payload.get("required_specialty", "general")

        appointment_id = f"SPECIALIST-{emergency_id}"

        self.agent.total_requests += 1

        self.agent.pending[specialty].append(
            {
                "appointment_id": appointment_id,
                "patient_jid": hospital_jid,  # aqui o "cliente" é o hospital
                "specialty": specialty,
                "reason": "specialist_request",
                "timestamp": payload.get("timestamp", get_current_time()),
                "mode": "specialist",
                "emergency_id": emergency_id,
            }
        )

        logger.info(f"[SCHED] queued specialist_request emergency_id={emergency_id} specialty={specialty}")

        await _try_assign_and_send(self)


async def _try_assign_and_send(beh):
    """
    Tenta atribuir um doctor e envia doctor_assign.
    """
    # tenta para todas as especialidades com fila
    for specialty in list(beh.agent.pending.keys()):
        out = beh.agent.try_assign(specialty)
        if not out:
            continue

        req, doctor_jid = out
        beh.agent.total_scheduled += 1

        assign_payload = {
            "appointment_id": req["appointment_id"],
            "patient_jid": req["patient_jid"],
            "specialty": specialty,
            "reason": req.get("reason"),
            "timestamp": get_current_time(),
            "mode": req.get("mode", "appointment"),
            "emergency_id": req.get("emergency_id"),
        }

        msg = build_spade_message(
            to=doctor_jid,
            performative=Performative.REQUEST,
            msg_type=AppointmentMsg.DOCTOR_ASSIGN,
            payload=assign_payload,
        )
        await beh.send(msg)
        logger.info(f"[SCHED] Assigned doctor={doctor_jid} appointment_id={req['appointment_id']}")
