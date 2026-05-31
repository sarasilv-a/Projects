from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.protocols import AppointmentMsg
from core.spade_utils import parse_spade_message
from core.utils import logger, get_current_time

class HandleDoctorDoneBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != AppointmentMsg.DOCTOR_DONE.value:
            return

        appointment_id = payload.get("appointment_id")
        rec = self.agent.active.get(appointment_id)
        if not rec:
            logger.warning(f"[SCHED] doctor_done unknown appointment_id: {payload}")
            return

        rec["status"] = "completed"
        rec["completed_at"] = get_current_time()
        self.agent.total_completed += 1

        logger.info(f"[SCHED] Completed appointment_id={appointment_id} rec={rec}")
        del self.agent.active[appointment_id]
