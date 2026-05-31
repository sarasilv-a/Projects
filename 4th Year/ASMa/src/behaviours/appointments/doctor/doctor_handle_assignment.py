from __future__ import annotations

import asyncio
from spade.behaviour import CyclicBehaviour
from core.config import SCHEDULER_JID
from core.protocols import Performative, AppointmentMsg, SpecialistMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class DoctorHandleAssignmentBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != AppointmentMsg.DOCTOR_ASSIGN.value:
            return

        sender_sched = str(msg.sender)
        appointment_id = payload.get("appointment_id")
        patient_jid = payload.get("patient_jid")
        specialty = payload.get("specialty", "general")
        mode = payload.get("mode", "appointment")
        emergency_id = payload.get("emergency_id")

        if not self.agent.available:
            refuse_payload = {"appointment_id": appointment_id, "reason": "doctor_busy", "timestamp": get_current_time()}
            refuse = build_spade_message(
                to=sender_sched,
                performative=Performative.REFUSE,
                msg_type="doctor_refuse", 
                payload=refuse_payload,
            )
            await self.send(refuse)
            return

        # aceitar
        self.agent.available = False
        self.agent.current_appointment_id = appointment_id

        # informar cliente
        scheduled_payload = {
            "appointment_id": appointment_id,
            "doctor_jid": str(self.agent.jid),
            "specialty": self.agent.specialty,
            "status": "scheduled",
            "timestamp": get_current_time(),
            "mode": mode,
            "emergency_id": emergency_id,
        }
        scheduled = build_spade_message(
            to=patient_jid,
            performative=Performative.INFORM,
            msg_type=AppointmentMsg.APPOINTMENT_SCHEDULED,
            payload=scheduled_payload,
        )
        await self.send(scheduled)

        # simular consulta/tratamento
        await asyncio.sleep(5)
        self.agent.total_consultations += 1

        done_payload = {
            "appointment_id": appointment_id,
            "doctor_jid": str(self.agent.jid),
            "status": "completed",
            "timestamp": get_current_time(),
            "mode": mode,
            "emergency_id": emergency_id,
        }

        # se for especialista, envia update ao hospital
        if mode == "specialist" and emergency_id:
            update_payload = {
                "emergency_id": emergency_id,
                "doctor_jid": str(self.agent.jid),
                "specialty": specialty,
                "note": "Specialist treatment completed",
                "timestamp": get_current_time(),
            }
            upd = build_spade_message(
                to=patient_jid,  # aqui patient_jid é hospital_jid no specialist mode
                performative=Performative.INFORM,
                msg_type=SpecialistMsg.TREATMENT_UPDATE,
                payload=update_payload,
            )
            await self.send(upd)

        # avisar scheduler
        done_sched = build_spade_message(
            to=sender_sched,
            performative=Performative.INFORM,
            msg_type=AppointmentMsg.DOCTOR_DONE,
            payload=done_payload,
        )
        await self.send(done_sched)

        # libertar
        self.agent.available = True
        self.agent.current_appointment_id = None

        # re-avisar disponibilidade
        avail_payload = {
            "doctor_jid": str(self.agent.jid),
            "specialty": self.agent.specialty,
            "available": True,
            "timestamp": get_current_time(),
        }
        avail = build_spade_message(
            to=SCHEDULER_JID,
            performative=Performative.INFORM,
            msg_type=AppointmentMsg.DOCTOR_AVAILABLE,
            payload=avail_payload,
        )
        await self.send(avail)
