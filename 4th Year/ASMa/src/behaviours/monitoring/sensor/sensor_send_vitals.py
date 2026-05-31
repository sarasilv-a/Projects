from __future__ import annotations

import random
from typing import Any, Dict
from spade.behaviour import PeriodicBehaviour
from core.config import MONITORING_JID
from core.protocols import Performative, MonitoringMsg
from core.spade_utils import build_spade_message
from core.utils import logger, get_current_time

class SensorSendVitalsBehaviour(PeriodicBehaviour):
    """Gera sinais vitais com distribuição mais realista para a demo.

    - Maioria das amostras: normal/levemente alterado
    - Algumas amostras: episódios críticos (para testar o fluxo)
    """

    def _sample_vitals(self) -> Dict[str, Any]:
        # 12% de probabilidade de evento crítico
        critical = random.random() < 0.12

        if critical:
            hr = random.randint(130, 170)
            spo2 = random.randint(78, 89)
            syst = random.randint(75, 95)
            dias = random.randint(45, 110)
        else:
            hr = int(random.gauss(82, 12))
            hr = max(55, min(125, hr))

            spo2 = int(random.gauss(96, 2))
            spo2 = max(90, min(100, spo2))

            syst = int(random.gauss(122, 15))
            syst = max(90, min(165, syst))

            dias = int(random.gauss(78, 10))
            dias = max(55, min(105, dias))

        return {"hr": hr, "spo2": spo2, "bp": f"{syst}/{dias}"}

    async def run(self):
        payload: Dict[str, Any] = {
            "patient_id": self.agent.patient_id,
            "timestamp": get_current_time(),
            "vitals": self._sample_vitals(),
        }

        msg = build_spade_message(
            to=MONITORING_JID,
            performative=Performative.INFORM,
            msg_type=MonitoringMsg.VITALS_UPDATE,
            payload=payload,
        )
        await self.send(msg)
        logger.info(f"[SENSOR] Sent vitals_update: {payload}")
