from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.spade_utils import parse_spade_message
from core.protocols import SpecialistMsg
from core.utils import logger

class HospitalHandleTreatmentUpdateBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != SpecialistMsg.TREATMENT_UPDATE.value:
            return

        emergency_id = payload.get("emergency_id")
        logger.info(f"[HOSPITAL] treatment_update emergency_id={emergency_id} payload={payload}")

        if emergency_id in self.agent.admitted:
            self.agent.admitted[emergency_id]["treatment_update"] = payload
