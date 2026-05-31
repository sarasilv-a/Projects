from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Deque, Dict, Optional, Tuple
from spade.agent import Agent
from spade.template import Template
from core.utils import logger
from core.protocols import MonitoringMsg
from behaviours.monitoring.monitoring.monitoring_receive_vitals import MonitoringReceiveVitalsBehaviour
from behaviours.monitoring.monitoring.monitoring_report import MonitoringReportBehaviour

@dataclass
class ActiveAlert:
    emergency_id: str
    last_alert_ts: datetime
    last_score: int

class MonitoringAgent(Agent):
    def __init__(
        self,
        jid: str,
        password: str,
        *,
        history_size: int = 10,
        alert_cooldown_seconds: int = 20,
    ):
        super().__init__(jid, password)
        self.history_size = history_size
        self.alert_cooldown_seconds = alert_cooldown_seconds

        # patient_id -> deque[(timestamp, vitals_dict)]
        self.history: Dict[str, Deque[Tuple[str, Dict[str, Any]]]] = defaultdict(
            lambda: deque(maxlen=self.history_size)
        )

        # patient_id -> ActiveAlert
        self.active_alerts: Dict[str, ActiveAlert] = {}

        self.total_updates = 0
        self.total_alerts = 0

    @staticmethod
    def _parse_ts(ts: Optional[str]) -> datetime:
        if not ts:
            return datetime.utcnow()
        try:
            # suporta ISO sem timezone
            return datetime.fromisoformat(ts)
        except Exception:
            return datetime.utcnow()

    def should_create_alert(self, patient_id: str, emergency_id: str, now_ts: datetime, score: int) -> bool:
        """Debounce:
        - Se não houver alerta ativo -> cria
        - Se houver, só cria se:
            a) passou cooldown
            OU
            b) score piorou bastante (>= last_score + 2)
        """
        active = self.active_alerts.get(patient_id)
        if not active:
            self.active_alerts[patient_id] = ActiveAlert(emergency_id=emergency_id, last_alert_ts=now_ts, last_score=score)
            return True

        delta = (now_ts - active.last_alert_ts).total_seconds()

        if delta >= self.alert_cooldown_seconds or score >= active.last_score + 2:
            self.active_alerts[patient_id] = ActiveAlert(emergency_id=emergency_id, last_alert_ts=now_ts, last_score=score)
            return True

        return False

    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", MonitoringMsg.VITALS_UPDATE.value)
        self.add_behaviour(MonitoringReceiveVitalsBehaviour(), tpl)

        self.add_behaviour(MonitoringReportBehaviour(period=10))

        logger.info(f"[MONITOR] Agent started: {self.jid}")
