from __future__ import annotations
import asyncio
from core.config import account, AMBULANCE_JIDS, HOSPITAL_JIDS
from agents.monitoring.monitoring_agent import MonitoringAgent
from agents.monitoring.sensor_agent import SensorAgent
from agents.emergency.emergency_center_agent import EmergencyCenterAgent
from agents.emergency.triage_agent import TriageAgent
from agents.emergency.hospital_agent import HospitalAgent
from agents.emergency.ambulance_agent import AmbulanceAgent

def banner():
    print("=" * 70)
    print("DEMO: MONITORING -> ALERT -> EMERGENCY (monitoring + sensor + emergency pipeline)")
    print("=" * 70)
    print()

async def safe_stop(agent, *, name: str = "", timeout: float = 5.0):
    if agent is None:
        return
    try:
        await asyncio.wait_for(agent.stop(), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"[STOP] timeout a parar {name or str(agent)} (continuo...)")
    except Exception as e:
        print(f"[STOP] erro a parar {name or str(agent)}: {e}")

async def main():
    banner()

    monitoring = sensor = center = triage = None
    hospitals, ambulances = [], []
    RUN_SECONDS = 45

    try:
        center_acc = account("emergency_center")
        center = EmergencyCenterAgent(center_acc.jid, center_acc.password)
        await center.start()

        triage_acc = account("triage")
        triage = TriageAgent(triage_acc.jid, triage_acc.password)
        await triage.start()

        for i, _ in enumerate(HOSPITAL_JIDS[:1], start=1):
            acc = account("hospital" if i == 1 else f"hospital{i}")
            a = HospitalAgent(acc.jid, acc.password)
            hospitals.append(a)
            await a.start()

        for i, _ in enumerate(AMBULANCE_JIDS[:1], start=1):
            acc = account("ambulance" if i == 1 else f"ambulance{i}")
            a = AmbulanceAgent(acc.jid, acc.password)
            ambulances.append(a)
            await a.start()

        # monitoring
        mon_acc = account("monitoring")
        monitoring = MonitoringAgent(mon_acc.jid, mon_acc.password, alert_cooldown_seconds=10)
        await monitoring.start()

        sensor_acc = account("sensor")
        sensor = SensorAgent(sensor_acc.jid, sensor_acc.password, patient_id="P-MON")
        await sensor.start()

        await asyncio.sleep(RUN_SECONDS)

    finally:
        await safe_stop(sensor, name="sensor")
        await safe_stop(monitoring, name="monitoring")
        for idx, a in enumerate(ambulances, start=1):
            await safe_stop(a, name=f"ambulance{idx}")
        for idx, h in enumerate(hospitals, start=1):
            await safe_stop(h, name=f"hospital{idx}")
        await safe_stop(triage, name="triage")
        await safe_stop(center, name="center")
        print("[MONITORING->EMERGENCY] finished")
        await asyncio.sleep(0.5)
        raise SystemExit(0)


if __name__ == "__main__":
    asyncio.run(main())
