from __future__ import annotations

from datetime import datetime
from spade.behaviour import CyclicBehaviour
from core.config import EMERGENCY_CENTER_JID
from core.protocols import Performative, MonitoringMsg, EmergencyMsg
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, format_emergency_id, get_current_time

def vitals_score(vitals) -> int:
    """Score simples (0..10) para decidir severidade/piora.

    Heurística (mínima e estável para demo):
    - HR > 130 -> +2
    - HR > 150 -> +1 extra
    - SpO2 < 90 -> +3
    - SpO2 < 85 -> +1 extra
    - Sistólica < 90 -> +3
    - Sistólica < 80 -> +1 extra
    Caps em 10.
    """
    # HR
    try:
        hr = int(vitals.get("hr", 0))
    except Exception:
        hr = 0

    # SpO2
    try:
        spo2 = int(vitals.get("spo2", 100))
    except Exception:
        spo2 = 100

    # BP sistólica
    bp = vitals.get("bp", "120/80")
    try:
        syst = int(str(bp).split("/")[0])
    except Exception:
        syst = 120

    score = 0
    if hr > 130:
        score += 2
    if hr > 150:
        score += 1

    if spo2 < 90:
        score += 3
    if spo2 < 85:
        score += 1

    if syst < 90:
        score += 3
    if syst < 80:
        score += 1

    return min(score, 10)


def is_critical(vitals) -> bool:
    """Regras base"""
    try:
        hr = int(vitals.get("hr", 0))
    except Exception:
        hr = 0

    try:
        spo2 = int(vitals.get("spo2", 100))
    except Exception:
        spo2 = 100

    bp = vitals.get("bp", "120/80")
    try:
        syst = int(str(bp).split("/")[0])
    except Exception:
        syst = 120

    return (spo2 < 90) or (hr > 130) or (syst < 90)


class MonitoringReceiveVitalsBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != MonitoringMsg.VITALS_UPDATE.value:
            return

        patient_id = payload.get("patient_id", "unknown")
        timestamp = payload.get("timestamp")
        vitals = payload.get("vitals", {})

        self.agent.total_updates += 1
        self.agent.history[patient_id].append((timestamp, vitals))

        logger.info(f"[MONITOR] vitals_update patient={patient_id} vitals={vitals}")

        if not is_critical(vitals):
            return

        # Debounce: 1 alerta ativo por patient_id
        score = vitals_score(vitals)
        ts_str = get_current_time()
        emergency_id = format_emergency_id(patient_id, ts_str)
        now_dt = self.agent._parse_ts(ts_str)

        if not self.agent.should_create_alert(patient_id, emergency_id, now_dt, score):
            # mantém comportamento observável mas sem criar emergências em loop
            logger.warning(
                f"[MONITOR] CRITICAL but debounced patient={patient_id} score={score} vitals={vitals}"
            )
            return

        self.agent.total_alerts += 1

        alert_payload = {
            "patient_id": patient_id,
            "patient_name": f"Patient {patient_id}",
            "emergency_id": emergency_id,
            "location": "UNKNOWN",
            "severity": max(6, min(10, score)),
            "description": "Critical vitals detected by monitoring",
            "vitals": vitals,
            "timestamp": ts_str,
            "source": "monitoring",
        }

        alert = build_spade_message(
            to=EMERGENCY_CENTER_JID,
            performative=Performative.REQUEST,
            msg_type=EmergencyMsg.EMERGENCY_ALERT,
            payload=alert_payload,
        )
        await self.send(alert)
        logger.warning(f"[MONITOR] REQUEST emergency_alert: {alert_payload}")
