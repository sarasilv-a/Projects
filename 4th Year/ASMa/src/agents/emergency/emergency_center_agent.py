from __future__ import annotations

from typing import Any, Dict, List, Optional
from spade.agent import Agent
from spade.template import Template
from core.protocols import EmergencyMsg
from core.utils import logger
from behaviours.emergency.center.center_receive_alerts import ReceiveEmergencyAlertsBehaviour
from behaviours.emergency.center.center_handle_triage import HandleTriageResultBehaviour
from behaviours.emergency.center.center_handle_updates import HandleUpdatesBehaviour
from behaviours.emergency.center.center_handle_status import HandleStatusQueriesBehaviour
from behaviours.emergency.center.center_report import CenterReportBehaviour

class EmergencyCenterAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self.active_emergencies: Dict[str, Dict[str, Any]] = {}

        self._rr_hospital = 0
        self._rr_ambulance = 0
        self._rr_helicopter = 0

    @staticmethod
    def _pick_rr(items: List[str], idx: int) -> tuple[str, int]:
        if not items:
            raise ValueError("No items to pick")
        chosen = items[idx % len(items)]
        return chosen, (idx + 1) % len(items)

    def pick_hospital(self, hospitals: List[str], avoid: Optional[List[str]] = None) -> Optional[str]:
        avoid = avoid or []
        if not hospitals:
            return None

        for _ in range(len(hospitals)):
            jid, self._rr_hospital = self._pick_rr(hospitals, self._rr_hospital)
            if jid not in avoid:
                return jid
        return None

    def pick_helicopter(self, helicopters: List[str]) -> Optional[str]:
        if not helicopters:
            return None
        jid, self._rr_helicopter = self._pick_rr(helicopters, self._rr_helicopter)
        return jid

    def pick_ambulance(self, ambulances: List[str]) -> Optional[str]:
        if not ambulances:
            return None
        jid, self._rr_ambulance = self._pick_rr(ambulances, self._rr_ambulance)
        return jid

    async def setup(self):
        # Receber emergency_alert
        tpl1 = Template()
        tpl1.set_metadata("type", EmergencyMsg.EMERGENCY_ALERT.value)
        self.add_behaviour(ReceiveEmergencyAlertsBehaviour(), tpl1)

        # Receber triage_result
        tpl2 = Template()
        tpl2.set_metadata("type", EmergencyMsg.TRIAGE_RESULT.value)
        self.add_behaviour(HandleTriageResultBehaviour(), tpl2)

        # Updates de transport/hospital
        for t in (
            EmergencyMsg.TRANSPORT_JOB_DONE.value,
            EmergencyMsg.PATIENT_ADMITTED.value,
            EmergencyMsg.PATIENT_REFUSED.value,
            EmergencyMsg.TRANSPORT_REFUSE.value,
            EmergencyMsg.TRANSPORT_ACCEPT.value,
        ):
            tpl = Template()
            tpl.set_metadata("type", t)
            self.add_behaviour(HandleUpdatesBehaviour(), tpl)

        # status queries
        tplS = Template()
        tplS.set_metadata("type", EmergencyMsg.EMERGENCY_STATUS_REQ.value)
        self.add_behaviour(HandleStatusQueriesBehaviour(), tplS)

        # report
        self.add_behaviour(CenterReportBehaviour(period=10))

        logger.info(f"[CENTER] Agent started: {self.jid}")
