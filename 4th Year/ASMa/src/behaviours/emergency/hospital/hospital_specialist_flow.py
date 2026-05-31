from __future__ import annotations

from spade.behaviour import PeriodicBehaviour
from core.config import SCHEDULER_JID
from core.protocols import Performative, SpecialistMsg
from core.spade_utils import build_spade_message
from core.utils import logger, get_current_time

class HospitalSpecialistFlowBehaviour(PeriodicBehaviour):
    """
    Periodicamente verifica se há casos admitidos que requerem especialidade != general
    e pede especialista ao Scheduler.
    """
    async def run(self):
        for emergency_id, rec in list(self.agent.admitted.items()):
            specialty = rec.get("required_specialty", "general")
            if specialty == "general":
                continue

            # se já pediu, não volta a pedir
            if rec.get("specialist_requested"):
                continue

            payload = {
                "emergency_id": emergency_id,
                "required_specialty": specialty,
                "timestamp": get_current_time(),
            }
            msg = build_spade_message(
                to=SCHEDULER_JID,
                performative=Performative.REQUEST,
                msg_type=SpecialistMsg.SPECIALIST_REQUEST,
                payload=payload,
            )
            await self.send(msg)

            rec["specialist_requested"] = True
            logger.info(f"[HOSPITAL] REQUEST specialist_request emergency_id={emergency_id} specialty={specialty}")
