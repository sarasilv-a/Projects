from __future__ import annotations
import asyncio
from core.config import account, AMBULANCE_JIDS, HELICOPTER_JIDS, HOSPITAL_JIDS
from agents.emergency.emergency_center_agent import EmergencyCenterAgent
from agents.emergency.triage_agent import TriageAgent
from agents.emergency.hospital_agent import HospitalAgent
from agents.emergency.ambulance_agent import AmbulanceAgent
from agents.emergency.helicopter_agent import HelicopterAgent
from agents.emergency.patient_agent import PatientAgent


def banner():
    print("=" * 70)
    print("DEMO: EMERGENCY BASIC (center + triage + transport + hospital + 1 patient)")
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

    center = triage = patient = None
    hospitals, ambulances, helicopters = [], [], []
    RUN_SECONDS = 35

    try:
        center_acc = account("emergency_center")
        center = EmergencyCenterAgent(center_acc.jid, center_acc.password)
        await center.start()

        triage_acc = account("triage")
        triage = TriageAgent(triage_acc.jid, triage_acc.password)
        await triage.start()

        # 1-2 hospitais
        for i, _ in enumerate(HOSPITAL_JIDS[:2], start=1):
            username = "hospital" if i == 1 else f"hospital{i}"
            acc = account(username)
            a = HospitalAgent(acc.jid, acc.password)
            hospitals.append(a)
            await a.start()

        # 1-2 ambulâncias
        for i, _ in enumerate(AMBULANCE_JIDS[:2], start=1):
            username = "ambulance" if i == 1 else f"ambulance{i}"
            acc = account(username)
            a = AmbulanceAgent(acc.jid, acc.password)
            ambulances.append(a)
            await a.start()

        # 1 helicóptero (opcional)
        for i, _ in enumerate(HELICOPTER_JIDS[:1], start=1):
            username = "helicopter" if i == 1 else f"helicopter{i}"
            acc = account(username)
            a = HelicopterAgent(acc.jid, acc.password)
            helicopters.append(a)
            await a.start()

        # paciente emergência
        pat_acc = account("patient_emergency")
        patient = PatientAgent(
            pat_acc.jid,
            pat_acc.password,
            patient_id="P001",
            name="Alice",
        )
        await patient.start()

        await asyncio.sleep(RUN_SECONDS)

    finally:
        await safe_stop(patient, name="patient")
        for idx, h in enumerate(helicopters, start=1):
            await safe_stop(h, name=f"helicopter{idx}")
        for idx, a in enumerate(ambulances, start=1):
            await safe_stop(a, name=f"ambulance{idx}")
        for idx, h in enumerate(hospitals, start=1):
            await safe_stop(h, name=f"hospital{idx}")
        await safe_stop(triage, name="triage")
        await safe_stop(center, name="center")
        print("[EMERGENCY BASIC] finished")
        await asyncio.sleep(0.5)
        raise SystemExit(0)


if __name__ == "__main__":
    asyncio.run(main())
