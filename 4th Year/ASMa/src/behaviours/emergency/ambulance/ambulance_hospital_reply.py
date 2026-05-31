from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import Performative, EmergencyMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class AmbulanceHospitalReplyBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        emergency_id = payload.get("emergency_id")

        logger.info(f"[AMBULANCE] Hospital reply perf={perf} type={mtype} payload={payload}")

        # Propaga admitted/refused ao CENTER
        if self.agent.center_jid:
            fwd = build_spade_message(
                to=self.agent.center_jid,
                performative=Performative.CONFIRM if mtype == EmergencyMsg.PATIENT_ADMITTED.value else Performative.REFUSE,
                msg_type=EmergencyMsg.PATIENT_ADMITTED if mtype == EmergencyMsg.PATIENT_ADMITTED.value else EmergencyMsg.PATIENT_REFUSED,
                payload=payload,
            )
            await self.send(fwd)

        # Só mexe no estado se for o emergency atual
        if emergency_id and (emergency_id != self.agent.current_emergency_id):
            return

        if mtype == EmergencyMsg.PATIENT_ADMITTED.value:
            done_payload = {
                "emergency_id": emergency_id,
                "transport_type": "ambulance",
                "timestamp": get_current_time(),
            }
            if self.agent.center_jid:
                done = build_spade_message(
                    to=self.agent.center_jid,
                    performative=Performative.INFORM,
                    msg_type=EmergencyMsg.TRANSPORT_JOB_DONE,
                    payload=done_payload,
                )
                await self.send(done)

            self.agent.total_jobs += 1
            self.agent.available = True
            self.agent.current_emergency_id = None
            self.agent.center_jid = None

        elif mtype == EmergencyMsg.PATIENT_REFUSED.value:
            if payload.get("status") == "hospital_full":
                return

            done_payload = {
                "emergency_id": emergency_id,
                "transport_type": "ambulance",
                "timestamp": get_current_time(),
            }
            if self.agent.center_jid:
                done = build_spade_message(
                    to=self.agent.center_jid,
                    performative=Performative.INFORM,
                    msg_type=EmergencyMsg.TRANSPORT_JOB_DONE,
                    payload=done_payload,
                )
                await self.send(done)

            self.agent.available = True
            self.agent.current_emergency_id = None
            self.agent.center_jid = None
